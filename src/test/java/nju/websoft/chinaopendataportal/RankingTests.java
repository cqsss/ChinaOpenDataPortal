package nju.websoft.chinaopendataportal;

import javafx.util.Pair;
import nju.websoft.chinaopendataportal.Ranking.MMRTest;
import nju.websoft.chinaopendataportal.Ranking.RelevanceRanking;
import org.apache.lucene.search.similarities.BM25Similarity;
import org.apache.lucene.search.similarities.ClassicSimilarity;
import org.apache.lucene.search.similarities.LMDirichletSimilarity;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;

import java.util.List;
import java.util.Map;

@SpringBootTest
public class RankingTests {
    private final RelevanceRanking relevanceRanking = new RelevanceRanking();
    private final MMRTest mmrTest = new MMRTest();

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Test
    public void testRelevanceRanking() throws Exception {

        List<Map<String, Object>> queryList = jdbcTemplate.queryForList("SELECT * FROM query ORDER BY query_id");
        for (Map<String, Object> qi : queryList) {
            int queryId = Integer.parseInt(qi.get("query_ID").toString());
            String query = qi.get("query_text").toString();
            String sql = "INSERT INTO results VALUES(?, ?, ?, ?, ?, ?)";

            List<Pair<Integer, Double>> scoreList = relevanceRanking.LuceneRankingList(query, new BM25Similarity(),
                    GlobalVariances.BoostWeights);
            for (int i = 0; i < Math.min(GlobalVariances.ExperimentSize, scoreList.size()); i++) {
                jdbcTemplate.update(sql, queryId, scoreList.get(i).getKey(), scoreList.get(i).getValue(), i + 1, "BM25",
                        null);
            }
            for (int k = 10; k <= 50; k += 10) {
                List<Pair<Integer, Double>> resultList = mmrTest.reRankList(scoreList, k);
                for (int i = 0; i < Math.min(GlobalVariances.ExperimentSize, resultList.size()); i++) {
                    jdbcTemplate.update(sql, queryId, resultList.get(i).getKey(), resultList.get(i).getValue(), i + 1,
                            "BM25+MMR" + k, null);
                }
            }

            scoreList = relevanceRanking.LuceneRankingList(query, new ClassicSimilarity(),
                    GlobalVariances.BoostWeights);
            for (int i = 0; i < Math.min(GlobalVariances.ExperimentSize, scoreList.size()); i++) {
                jdbcTemplate.update(sql, queryId, scoreList.get(i).getKey(), scoreList.get(i).getValue(), i + 1,
                        "TFIDF", null);
            }
            for (int k = 10; k <= 50; k += 10) {
                List<Pair<Integer, Double>> resultList = mmrTest.reRankList(scoreList, k);
                for (int i = 0; i < Math.min(GlobalVariances.ExperimentSize, resultList.size()); i++) {
                    jdbcTemplate.update(sql, queryId, resultList.get(i).getKey(), resultList.get(i).getValue(), i + 1,
                            "TFIDF+MMR" + k, null);
                }
            }

            scoreList = relevanceRanking.LuceneRankingList(query, new LMDirichletSimilarity(),
                    GlobalVariances.BoostWeights);
            for (int i = 0; i < Math.min(GlobalVariances.ExperimentSize, scoreList.size()); i++) {
                jdbcTemplate.update(sql, queryId, scoreList.get(i).getKey(), scoreList.get(i).getValue(), i + 1, "LMD",
                        null);
            }
            for (int k = 10; k <= 50; k += 10) {
                List<Pair<Integer, Double>> resultList = mmrTest.reRankList(scoreList, k);
                for (int i = 0; i < Math.min(GlobalVariances.ExperimentSize, resultList.size()); i++) {
                    jdbcTemplate.update(sql, queryId, resultList.get(i).getKey(), resultList.get(i).getValue(), i + 1,
                            "LMD+MMR" + k, null);
                }
            }
            System.out.println("query_id: " + queryId);
        }
    }

    @Test
    public void testRunTime() throws Exception {

        List<Map<String, Object>> queryList = jdbcTemplate.queryForList("SELECT * FROM query ORDER BY query_id");
        for (Map<String, Object> qi : queryList) {
            int queryId = Integer.parseInt(qi.get("query_ID").toString());
            String query = qi.get("query_text").toString();
            String sql = "UPDATE results SET run_time=? WHERE query_id=? AND method=?";
            long startTime = System.currentTimeMillis();
            List<Pair<Integer, Double>> scoreList = relevanceRanking.LuceneRankingList(query, new BM25Similarity(),
                    GlobalVariances.BoostWeights);
            long endTime = System.currentTimeMillis();
            long totalTime = endTime - startTime;
            jdbcTemplate.update(sql, totalTime, queryId, "BM25");
            for (int k = 10; k <= 50; k += 10) {
                startTime = System.currentTimeMillis();
                List<Pair<Integer, Double>> resultList = mmrTest.reRankList(scoreList, k);
                endTime = System.currentTimeMillis();
                totalTime = endTime - startTime;
                jdbcTemplate.update(sql, totalTime, queryId, "BM25+MMR" + k);
            }

            startTime = System.currentTimeMillis();
            scoreList = relevanceRanking.LuceneRankingList(query, new ClassicSimilarity(),
                    GlobalVariances.BoostWeights);
            endTime = System.currentTimeMillis();
            totalTime = endTime - startTime;
            jdbcTemplate.update(sql, totalTime, queryId, "TFIDF");
            for (int k = 10; k <= 50; k += 10) {
                startTime = System.currentTimeMillis();
                List<Pair<Integer, Double>> resultList = mmrTest.reRankList(scoreList, k);
                endTime = System.currentTimeMillis();
                totalTime = endTime - startTime;
                jdbcTemplate.update(sql, totalTime, queryId, "TFIDF+MMR" + k);
            }

            startTime = System.currentTimeMillis();
            scoreList = relevanceRanking.LuceneRankingList(query, new LMDirichletSimilarity(),
                    GlobalVariances.BoostWeights);
            endTime = System.currentTimeMillis();
            totalTime = endTime - startTime;
            jdbcTemplate.update(sql, totalTime, queryId, "LMD");
            for (int k = 10; k <= 50; k += 10) {
                startTime = System.currentTimeMillis();
                List<Pair<Integer, Double>> resultList = mmrTest.reRankList(scoreList, k);
                endTime = System.currentTimeMillis();
                totalTime = endTime - startTime;
                jdbcTemplate.update(sql, totalTime, queryId, "LMD+MMR" + k);
            }
            System.out.println("query_id: " + queryId);
        }
    }
}
