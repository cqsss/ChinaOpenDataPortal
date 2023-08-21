package nju.websoft.chinaopendataportal.Controller;

import javafx.util.Pair;
import nju.websoft.chinaopendataportal.Bean.Metadata;
import nju.websoft.chinaopendataportal.Ranking.MMRTest;
import nju.websoft.chinaopendataportal.GlobalVariances;
import nju.websoft.chinaopendataportal.Ranking.RelevanceRanking;
import nju.websoft.chinaopendataportal.Service.MetadataService;
import nju.websoft.chinaopendataportal.Service.QrelService;
import nju.websoft.chinaopendataportal.Service.QueryService;
import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.TokenStream;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.Term;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.*;
import org.apache.lucene.search.highlight.*;
import org.apache.lucene.search.similarities.BM25Similarity;
import org.apache.lucene.search.similarities.ClassicSimilarity;
import org.apache.lucene.search.similarities.LMDirichletSimilarity;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.MMapDirectory;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.io.StringReader;
import java.lang.reflect.Field;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.nio.file.Paths;
import java.util.*;

@Controller
public class SearchController {

    private final RelevanceRanking relevanceRanking = new RelevanceRanking();
    private final MetadataService metadataService;
    private final QueryService queryService;
    private final QrelService qrelService;
    private final MMRTest mmrTest = new MMRTest();
    private Directory directory = null;
    private IndexReader indexReader = null;
    private IndexSearcher indexSearcher = null;
    private String current_query = "";

    public SearchController(MetadataService metadataService, QueryService queryService, QrelService qrelService) {
        this.metadataService = metadataService;
        this.queryService = queryService;
        this.qrelService = qrelService;
    }

    private void init() {
        try {
            if (directory == null) {
                directory = MMapDirectory.open(Paths.get(GlobalVariances.index_Dir));
                indexReader = DirectoryReader.open(directory);
                indexSearcher = new IndexSearcher(indexReader);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @RequestMapping("/search")
    public String starter() {
        return "search.html";
    }

    @RequestMapping(value = "/dosearch", method = RequestMethod.POST)
    public String dosearch(@RequestParam("query") String query) {
        if (query.equals(""))
            query = current_query;
        query = URLEncoder.encode(query, StandardCharsets.UTF_8);
        query = query.replaceAll("\\+", "%20");
        return "redirect:/result?q=" + query + "&province=&city=&industry=&isopen=&page=1";
    }

    public String getHighlighter(String query, String fieldValues) throws ParseException, IOException, InvalidTokenOffsetsException {

        Analyzer analyzer = GlobalVariances.globalAnalyzer;
        QueryParser queryParser = new QueryParser("title", analyzer);
        query = QueryParser.escape(query);
        Query parsedQuery = queryParser.parse(query);
        Fragmenter fragmenter = new SimpleFragmenter(GlobalVariances.maxCharOfDescription);
        SimpleHTMLFormatter simpleHTMLFormatter = new SimpleHTMLFormatter("<span style='color:red'>", "</span>");
        Highlighter highlighter = new Highlighter(simpleHTMLFormatter, new QueryScorer(parsedQuery));
        highlighter.setTextFragmenter(fragmenter);
        TokenStream tokenStream = analyzer.tokenStream("", new StringReader(fieldValues));
        String res = highlighter.getBestFragment(tokenStream, fieldValues);
        if (res == null) {
            res = fieldValues;
            if (res.length() > GlobalVariances.maxCharOfDescription) {
                res = res.substring(0, GlobalVariances.maxCharOfDescription - 1);
                res += "...";
            }
        }
        return res;
    }

    @GetMapping(value = "/result")
    public String searchResult(@RequestParam("q") String query,
                               @RequestParam("province") String province,
                               @RequestParam("city") String city,
                               @RequestParam("industry") String industry,
                               @RequestParam("isopen") String isOpen,
                               @RequestParam("page") int page,
                               Model model) throws ParseException, IOException, InvalidTokenOffsetsException {
        init();
        String provinceView = province.equals("") ? "全部" : province;
        String cityView = city.equals("") ? "全部" : city;
        String industryView = industry.equals("") ? "全部" : industry;
        String isOpenView = isOpen.equals("") ? "全部" : isOpen;

        Map<String, String> filterMap = new HashMap<>();
        filterMap.put("province", province);
        filterMap.put("city", city);
        filterMap.put("industry", industry);
        filterMap.put("is_open", isOpen);

        List<String> provinceList = metadataService.getProvinces();
        provinceList.add(0, "全部");
        List<String> cityList = new ArrayList<>();
        if (!province.equals("")) {
            cityList = metadataService.getCitiesByProvince(province);
            cityList.add(0, "全部");
        }
        List<String> industryList = Arrays.asList(GlobalVariances.industryFields);
        List<String> isOpenList = Arrays.asList(GlobalVariances.isOpenFields);

        List<Map<String,String>> snippetList = new ArrayList<>();
        Map<String, Integer> relScoreMap = new HashMap<>();
        Analyzer analyzer = GlobalVariances.globalAnalyzer;
        QueryParser datasetIdParser = new QueryParser("dataset_id", analyzer);
        relevanceRanking.init();

        if (current_query.isEmpty() || !current_query.equals(query)) {
            current_query = query;
        }
        String queryURL = URLEncoder.encode(query, StandardCharsets.UTF_8);
        queryURL = queryURL.replaceAll("\\+", "%20");

        boolean inAnnotation = queryService.findQueryByText(query);
        int queryId = -1;
        if (inAnnotation) {
            queryId = (int) queryService.getQueryByText(query).getQuery_id();
        }

//        long totalHits = relevanceRanking.getTotalHits(query, new BM25Similarity(), GlobalVariances.BoostWeights, GlobalVariances.index_Dir);
        Pair<Long, List<Pair<Integer, Double>>> rankingResult = relevanceRanking.LuceneRanking(query, new BM25Similarity(), GlobalVariances.BoostWeights, filterMap, GlobalVariances.index_Dir);
        long totalHits = rankingResult.getKey();
        List<Pair<Integer, Double>> scoreList = rankingResult.getValue();
        scoreList = mmrTest.reRankList(scoreList, 30);
        for (int i = (page - 1) * GlobalVariances.numOfDatasetsPerPage; i < Math.min(totalHits, (long) page * GlobalVariances.numOfDatasetsPerPage); i++) {
            Map<String,String> snippet = new HashMap<>();
            Integer ds_id = scoreList.get(i).getKey();
            snippet.put("dataset_id", ds_id.toString());
            Query dataset_id = datasetIdParser.parse(ds_id.toString());
            TopDocs docsSearch = indexSearcher.search(dataset_id, 1);
            ScoreDoc[] scoreDocs = docsSearch.scoreDocs;
            int docID = scoreDocs[0].doc;
            Document doc = indexReader.storedFields().document(docID);
            String title = getHighlighter(query, doc.get("title"));
            snippet.put("title", title);

            String description = getHighlighter(query, doc.get("description"));
            snippet.put("description", description);

            for (String fi : GlobalVariances.snippetFields) {
                String text = "";
                if (doc.get(fi) != null) {
                    String[] fieldValues = doc.getValues(fi);
                    Set<String> fieldSet = new HashSet<>(Arrays.asList(fieldValues));
                    String fieldText = fieldSet.toString();
                    fieldText = fieldText.substring(1, fieldText.length() - 1);
                    if (fi.equals("province") || fi.equals("city")) {
                        text = fieldText;
                    } else {
                        text = getHighlighter(query, fieldText);
                    }
                }
                snippet.put(fi, text);

                long score = -1;
                if (inAnnotation && qrelService.findQrel(queryId, ds_id)) {
                    score = qrelService.getQrel(queryId, ds_id).getRel_score();
                }
                relScoreMap.put(ds_id.toString(), (int) score);
            }
            snippetList.add(snippet);
        }
//        int numResults = Math.min(30, (int) totalHits);
        int numResults = (int) totalHits;
        int totalPages = numResults / GlobalVariances.numOfDatasetsPerPage;
        if (numResults % GlobalVariances.numOfDatasetsPerPage != 0)
            totalPages++;
        int previousPage = Math.max(1, page - 1);
        int nextPage = Math.min(totalPages, page + 1);
        Map<Integer, Integer> pages = new HashMap<>();
        for (int i = 0; i < 10; i++) {
            if (page <= 5) {
                pages.put(i + 1, i + 1);
            } else if (page >= totalPages - 4) {
                pages.put(i + 1, totalPages + i - 9);
            } else {
                pages.put(i + 1, page + i - 5);
            }
        }

        model.addAttribute("provinceView", provinceView);
        model.addAttribute("cityView", cityView);
        model.addAttribute("industryView", industryView);
        model.addAttribute("isOpenView", isOpenView);
        model.addAttribute("province", province);
        model.addAttribute("city", city);
        model.addAttribute("industry", industry);
        model.addAttribute("isOpen", isOpen);
        model.addAttribute("provinceList", provinceList);
        model.addAttribute("cityList", cityList);
        model.addAttribute("industryList", industryList);
        model.addAttribute("isOpenList", isOpenList);
        model.addAttribute("snippets", snippetList);
        model.addAttribute("query", query);
        model.addAttribute("query_id", queryId);
        model.addAttribute("queryURL", queryURL);
        model.addAttribute("in_annotation", inAnnotation);
        model.addAttribute("rel_score_map", relScoreMap);
        model.addAttribute("page", page);
        model.addAttribute("pages", pages);
        model.addAttribute("previousPage", previousPage);
        model.addAttribute("nextPage", nextPage);
        model.addAttribute("totalHits", totalHits);
        model.addAttribute("totalPages", totalPages);
        return "resultlist.html";
    }

    @GetMapping(value = "/detail")
    public String getDetail(@RequestParam("dsid") Integer dataset_id,
                            Model model) {
        init();
        Metadata dataset = metadataService.getMetadataByDatasetId(dataset_id);
        Field[] fields = dataset.getClass().getDeclaredFields();
        for (Field field : fields) {
            field.setAccessible(true);
            try {
                if (field.get(dataset) == null) {
                    field.set(dataset, "");
                }
            } catch (IllegalAccessException e) {
                e.printStackTrace();
            }
        }
        model.addAttribute("dataset", dataset);
        model.addAttribute("dataset_id", dataset_id);
        return "detaildashboard.html";
    }

    @RequestMapping(value = "/rating", method = RequestMethod.POST)
    @ResponseBody
    public void rating(@RequestParam("qid") int queryId,
                       @RequestParam("dsid") int datasetId,
                       @RequestBody String rating) {
        String scoreString = rating.substring(rating.length() - 1);
        int score = -1;
        if (!scoreString.equals(""))
            score = Integer.parseInt(scoreString);
        if (qrelService.findQrel(queryId, datasetId)) {
            if (score >= 0)
                qrelService.updateRelScoreById(queryId, datasetId, score);
        } else {
            if (score >= 0)
                qrelService.insertQrel(queryId, datasetId, score);
        }

    }

}
