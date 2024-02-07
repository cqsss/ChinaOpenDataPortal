package nju.websoft.chinaopendataportal.Controller;

import java.io.IOException;
import java.lang.reflect.Field;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.apache.lucene.document.Document;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.search.highlight.InvalidTokenOffsetsException;
import org.apache.lucene.search.similarities.BM25Similarity;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;

import javafx.util.Pair;
import nju.websoft.chinaopendataportal.GlobalVariances;
import nju.websoft.chinaopendataportal.Model.Metadata;
import nju.websoft.chinaopendataportal.Model.Portal;
import nju.websoft.chinaopendataportal.Model.Component.Filter;
import nju.websoft.chinaopendataportal.Ranking.MMRTest;
import nju.websoft.chinaopendataportal.Ranking.RelevanceRanking;
import nju.websoft.chinaopendataportal.Service.MetadataService;
import nju.websoft.chinaopendataportal.Service.NewsService;
import nju.websoft.chinaopendataportal.Service.PortalService;
import nju.websoft.chinaopendataportal.Util.HtmlHelper;

@Controller
public class SearchController {

    @Autowired
    private RelevanceRanking relevanceRanking;

    @Autowired
    private final MetadataService metadataService;
    private final PortalService portalService;
    private final NewsService newsService;

    private final MMRTest mmrTest = new MMRTest();

    @Autowired
    private IndexReader indexReader;

    public SearchController(
            MetadataService metadataService,
            PortalService portalService,
            NewsService newsService) {
        this.metadataService = metadataService;
        this.portalService = portalService;
        this.newsService = newsService;
    }

    @RequestMapping("/")
    public String starter(Model model) {
        int totalCount = metadataService.getMetadataCount();
        int provinceCount = metadataService.getProvinceCount();
        int cityCount = metadataService.getCityCount();
        model.addAttribute("totalCount", DecimalFormat.getNumberInstance().format(totalCount));
        model.addAttribute("provinceCount", DecimalFormat.getNumberInstance().format(provinceCount));
        model.addAttribute("cityCount", DecimalFormat.getNumberInstance().format(cityCount));
        model.addAttribute("newsList", newsService.getTop5News());

        return "search.html";
    }

    @Deprecated
    @RequestMapping(value = "/dosearch", method = RequestMethod.POST)
    public String dosearch(@RequestParam("query") String query) {
        if (query.equals("")) {
            query = GlobalVariances.defaultQuery;
        }
        query = URLEncoder.encode(query, StandardCharsets.UTF_8);
        query = query.replaceAll("\\+", "%20");
        return "redirect:/result?q=" + query;
    }

    @GetMapping(value = "/result")
    public String searchResult(@RequestParam("q") String query,
            @RequestParam(required = false, defaultValue = "全部") String province,
            @RequestParam(required = false, defaultValue = "全部") String city,
            @RequestParam(required = false, defaultValue = "全部") String industry,
            @RequestParam(required = false, defaultValue = "全部") String isopen,
            @RequestParam(defaultValue = "1") int page,
            Model model) throws ParseException, IOException, InvalidTokenOffsetsException {

        Map<String, String> filterMap = new HashMap<>();
        filterMap.put("province", province);
        filterMap.put("city", city);
        filterMap.put("industry", industry);
        filterMap.put("is_open", isopen);

        List<Map<String, String>> snippetList = new ArrayList<>();
        Map<String, Integer> relScoreMap = new HashMap<>();

        String queryURL = URLEncoder.encode(query, StandardCharsets.UTF_8);
        queryURL = queryURL.replaceAll("\\+", "%20");

        Pair<Long, List<Pair<Integer, Double>>> rankingResult = relevanceRanking.LuceneRanking(query,
                new BM25Similarity(), GlobalVariances.BoostWeights, filterMap);
        long totalHits = rankingResult.getKey();
        List<Pair<Integer, Double>> scoreList = rankingResult.getValue();
        scoreList = mmrTest.reRankList(scoreList, GlobalVariances.reRankSize);
        for (int i = (page - 1) * GlobalVariances.numOfDatasetsPerPage; i < Math.min(totalHits,
                (long) page * GlobalVariances.numOfDatasetsPerPage); i++) {
            Map<String, String> snippet = new HashMap<>();
            Integer doc_id = scoreList.get(i).getKey();
            Document doc = indexReader.storedFields().document(doc_id);
            String title = HtmlHelper.getHighlighter(query, doc.get("title"));
            snippet.put("title", title);
            snippet.put("docId", String.valueOf(doc_id));

            String description = HtmlHelper.getHighlighter(query, doc.get("description"));
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
                    } else if (fi.equals("data_formats")) {
                        // TODO: temporary process of `data_format` field
                        text = fieldText.replaceAll("'|\\[|\\]", "");
                    } else {
                        text = HtmlHelper.getHighlighter(query, fieldText);
                    }
                }
                snippet.put(fi, text);
            }
            if (snippet.get("province").equals(snippet.get("city"))) {
                snippet.put("city", "");
            }
            snippetList.add(snippet);
        }
        int numResults = Math.min(GlobalVariances.reRankSize, (int) totalHits);
        // int numResults = (int) totalHits;
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

        List<Filter> filters = new ArrayList<>();
        filters.add(new Filter("省份", province, "province", metadataService.getProvinces()));
        filters.add(new Filter("城市", city, "city", metadataService.getCitiesByProvince(province)));
        filters.add(new Filter("行业", industry, "industry", Arrays.asList(GlobalVariances.industryFields)));
        filters.add(new Filter("开放类型", isopen, "isopen", Arrays.asList(GlobalVariances.isOpenFields)));

        model.addAttribute("province", province);
        model.addAttribute("city", city);
        model.addAttribute("industry", industry);
        model.addAttribute("isOpen", isopen);
        model.addAttribute("filters", filters);
        model.addAttribute("snippets", snippetList);
        model.addAttribute("query", query);
        model.addAttribute("queryURL", queryURL);
        model.addAttribute("rel_score_map", relScoreMap);
        model.addAttribute("page", page);
        model.addAttribute("pages", pages);
        model.addAttribute("previousPage", previousPage);
        model.addAttribute("nextPage", nextPage);
        model.addAttribute("numResults", numResults);
        model.addAttribute("totalPages", totalPages);
        return "results.html";
    }

    @GetMapping(value = "/detail")
    public String getDetail(@RequestParam("docid") Integer docId, Model model) {
        try {
            Metadata dataset = metadataService.getMetadataByDocId(docId);
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
            Portal portal = portalService.getPortalByProvinceAndCity(dataset.province(), dataset.city());
            if (dataset.province().equals(dataset.city())) {
                dataset.city("");
            }
            if (dataset.url().equals("")) {
                dataset.url(portal.url());
            }
            model.addAttribute("dataset", dataset);
            model.addAttribute("portal", portal);
            model.addAttribute("docId", docId);
        } catch (Exception e) {
            e.printStackTrace();
        }
        return "detail.html";
    }

}
