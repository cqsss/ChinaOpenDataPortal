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

import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

@SpringBootTest
public class ExperimentTests {
    private RelevanceRanking relevanceRanking = new RelevanceRanking();
    private MMRTest mmrTest = new MMRTest();

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Test
    public void testRelevanceRanking() throws Exception {

        for (int topk = 5; topk <= 10; topk += 5) {

            System.out.println("top: " + topk);

            List<Map<String, Object>> queryList = jdbcTemplate.queryForList("SELECT * FROM query ORDER BY query_id");
            for (Map<String, Object> qi : queryList) {
                int queryId = Integer.parseInt(qi.get("query_ID").toString());
                String query = qi.get("query_text").toString();
                for (String m : new String[]{"BM25", "TFIDF", "LMD"}) {
                    String sql = "SELECT * FROM results WHERE query_id=? AND method=?";
                    List<Map<String, Object>> resultList = jdbcTemplate.queryForList(sql, queryId, m);
                    double totalSim = 0.0;
                    int simPairs = 0;
                    int mink = Math.min(resultList.size(), topk);
                    for (int i = 0; i < mink; i++) {
                        for (int j = i + 1; j < Math.min(resultList.size(), topk); j++) {
                            int dataset1 = (int) resultList.get(i).get("dataset_id");
                            int dataset2 = (int) resultList.get(j).get("dataset_id");
                            double sim = mmrTest.getSim2Score(dataset1, dataset2);
                            totalSim += sim;
                            if (sim > 0.5) {
                                simPairs++;
                            }
                        }
                    }
//                System.out.println(m + "\t" + totalSim / topk + "\t" + simPairs);
                    jdbcTemplate.update("INSERT INTO sim_metrics VALUES(?, ?, ?, ?, ?)", queryId, m, totalSim / (mink * (mink - 1) / 2), simPairs, topk);

                    for (int k = 10; k <= 50; k += 10) {
                        String method = m + "+MMR" + k;
                        resultList = jdbcTemplate.queryForList(sql, queryId, method);
                        totalSim = 0.0;
                        simPairs = 0;
                        for (int i = 0; i < mink; i++) {
                            for (int j = i + 1; j < Math.min(resultList.size(), topk); j++) {
                                int dataset1 = (int) resultList.get(i).get("dataset_id");
                                int dataset2 = (int) resultList.get(j).get("dataset_id");
                                double sim = mmrTest.getSim2Score(dataset1, dataset2);
                                totalSim += sim;
                                if (sim > 0.5) {
                                    simPairs++;
                                }
                            }
                        }
//                    System.out.println(method + "\t" + totalSim / topk + "\t" + simPairs);
                        jdbcTemplate.update("INSERT INTO sim_metrics VALUES(?, ?, ?, ?, ?)", queryId, method, totalSim / (mink * (mink - 1) / 2), simPairs, topk);
                    }
                }
                System.out.println("query_id: " + queryId);
            }
        }
    }
}
