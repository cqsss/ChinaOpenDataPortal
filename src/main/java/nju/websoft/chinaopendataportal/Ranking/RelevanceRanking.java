package nju.websoft.chinaopendataportal.Ranking;

import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.Term;
import org.apache.lucene.queryparser.classic.MultiFieldQueryParser;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.BooleanClause;
import org.apache.lucene.search.BooleanQuery;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TermQuery;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.search.similarities.Similarity;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.MMapDirectory;

import javafx.util.Pair;
import nju.websoft.chinaopendataportal.GlobalVariances;

public class RelevanceRanking {
    private static Directory directory = null;
    private static IndexReader indexReader = null;
    private static IndexSearcher indexSearcher = null;

    public void init() {
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

    public void init(String index_dir) {
        try {
            if (directory == null) {
                directory = MMapDirectory.open(Paths.get(index_dir));
                indexReader = DirectoryReader.open(directory);
                indexSearcher = new IndexSearcher(indexReader);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public long getTotalHits(String query, Similarity similarity, float[] weights, String index_dir) {
        long res = 0;
        init(index_dir);
        String[] fields = GlobalVariances.queryFields;
        try {
            Analyzer analyzer = GlobalVariances.globalAnalyzer;
            Map<String, Float> boosts = new HashMap<>();
            for (int i = 0; i < fields.length; i++) {
                boosts.put(fields[i], weights[i]);
            }
            QueryParser queryParser = new MultiFieldQueryParser(fields, analyzer, boosts);
            query = QueryParser.escape(query);
            Query parsedQuery = queryParser.parse(query);
            indexSearcher.setSimilarity(similarity);
            TopDocs docsSearch = indexSearcher.search(parsedQuery, 1);
            res = docsSearch.totalHits.value;
        } catch (Exception e) {
            e.printStackTrace();
        }
        return res;
    }

    /**
     * 得到根据Lucene分数排序后的列表
     *
     * @param query
     * @return
     */
    public Pair<Long, List<Pair<Integer, Double>>> LuceneRanking(String query, Similarity similarity, float[] weights,
            Map<String, String> filterQuery, String index_dir) {
        long res = 0;
        init(index_dir);
        String[] fields = GlobalVariances.queryFields;
        List<Pair<Integer, Double>> LuceneRankingList = new ArrayList<>();
        try {
            Analyzer analyzer = GlobalVariances.globalAnalyzer;
            Map<String, Float> boosts = new HashMap<>();
            for (int i = 0; i < fields.length; i++) {
                boosts.put(fields[i], weights[i]);
            }
            QueryParser fieldQueryParser = new MultiFieldQueryParser(fields, analyzer, boosts);
            query = QueryParser.escape(query);
            Query filedQuery = fieldQueryParser.parse(query);
            BooleanQuery.Builder finalQueryBuilder = new BooleanQuery.Builder().add(filedQuery,
                    BooleanClause.Occur.MUST);
            for (String filter : GlobalVariances.filterFields) {
                if (filterQuery.containsKey(filter) && filterQuery.get(filter).length() > 0
                        && !filterQuery.get(filter).equals("全部")) {
                    Query parsedFilterQuery = new TermQuery(new Term(filter, filterQuery.get(filter)));
                    finalQueryBuilder.add(parsedFilterQuery, BooleanClause.Occur.FILTER);
                }
            }
            Query finalQuery = finalQueryBuilder.build();
            indexSearcher.setSimilarity(similarity);
            TopDocs docsSearch = indexSearcher.search(finalQuery, GlobalVariances.HitSize);
            ScoreDoc[] scoreDocs = docsSearch.scoreDocs;
            res = docsSearch.totalHits.value;
            for (ScoreDoc si : scoreDocs) {
                int docID = si.doc;
                Set<String> fieldsToLoad = new HashSet<>();
                fieldsToLoad.add("dataset_id");
                Document document = indexReader.document(docID, fieldsToLoad);
                Integer datasetID = Integer.parseInt(document.get("dataset_id"));
                // System.out.println("dataset_id: " + document.get("dataset_id") + ", score: "
                // + si.score);
                // Explanation e = indexSearcher.explain(finalQuery, si.doc);
                // System.out.println("Explanation： \n" + e);
                LuceneRankingList.add(new Pair<>(datasetID, (double) si.score));
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return new Pair<>(res, LuceneRankingList);
    }

    public List<Pair<Integer, Double>> LuceneRankingList(String query, Similarity similarity, float[] weights,
            String index_dir) {
        init(index_dir);
        String[] fields = GlobalVariances.queryFields;
        List<Pair<Integer, Double>> LuceneRankingList = new ArrayList<>();
        try {
            Analyzer analyzer = GlobalVariances.globalAnalyzer;
            Map<String, Float> boosts = new HashMap<>();
            for (int i = 0; i < fields.length; i++) {
                boosts.put(fields[i], weights[i]);
            }
            QueryParser fieldQueryParser = new MultiFieldQueryParser(fields, analyzer, boosts);
            query = QueryParser.escape(query);
            Query filedQuery = fieldQueryParser.parse(query);
            indexSearcher.setSimilarity(similarity);
            TopDocs docsSearch = indexSearcher.search(filedQuery, GlobalVariances.HitSize);
            ScoreDoc[] scoreDocs = docsSearch.scoreDocs;
            for (ScoreDoc si : scoreDocs) {
                int docID = si.doc;
                Set<String> fieldsToLoad = new HashSet<>();
                fieldsToLoad.add("dataset_id");
                Document document = indexReader.document(docID, fieldsToLoad);
                Integer datasetID = Integer.parseInt(document.get("dataset_id"));
                // System.out.println("dataset_id: " + document.get("dataset_id") + ", score: "
                // + si.score);
                // Explanation e = indexSearcher.explain(parsedQuery, si.doc);
                // System.out.println("Explanation： \n" + e);
                LuceneRankingList.add(new Pair<>(datasetID, (double) si.score));
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return LuceneRankingList;
    }

    /**
     * 得到根据Lucene分数排序后的列表
     *
     * @param query
     * @return
     */
    public List<Pair<Integer, Double>> LuceneRankingList(String query, Similarity similarity, float[] weights,
            String index_dir, String[] fields) {
        init(index_dir);
        List<Pair<Integer, Double>> LuceneRankingList = new ArrayList<>();
        try {
            Analyzer analyzer = GlobalVariances.globalAnalyzer;
            Map<String, Float> boosts = new HashMap<>();
            for (int i = 0; i < fields.length; i++) {
                boosts.put(fields[i], weights[i]);
            }
            QueryParser queryParser = new MultiFieldQueryParser(fields, analyzer, boosts);
            query = QueryParser.escape(query);
            Query parsedQuery = queryParser.parse(query);
            indexSearcher.setSimilarity(similarity);
            TopDocs docsSearch = indexSearcher.search(parsedQuery, GlobalVariances.HitSize);
            ScoreDoc[] scoreDocs = docsSearch.scoreDocs;
            for (ScoreDoc si : scoreDocs) {
                int docID = si.doc;
                Set<String> fieldsToLoad = new HashSet<>();
                fieldsToLoad.add("dataset_id");
                Document document = indexReader.document(docID, fieldsToLoad);
                Integer datasetID = Integer.parseInt(document.get("dataset_id"));
                // System.out.println("dataset_id: " + document.get("dataset_id") + ", score: "
                // + si.score);
                // Explanation e = indexSearcher.explain(parsedQuery, si.doc);
                // System.out.println("Explanation： \n" + e);
                LuceneRankingList.add(new Pair<>(datasetID, (double) si.score));
            }
            // if (LuceneRankingList.size() > 0) {
            // double base = LuceneRankingList.get(0).getValue();
            // for (int i = 0; i < LuceneRankingList.size(); i++) {
            // LuceneRankingList.set(i, new Pair<>(LuceneRankingList.get(i).getKey(),
            // LuceneRankingList.get(i).getValue() / base));
            // }
            // }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return LuceneRankingList;
    }
}
