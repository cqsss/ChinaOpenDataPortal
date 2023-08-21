package nju.websoft.chinaopendataportal.Ranking;

import nju.websoft.chinaopendataportal.Bean.Metadata;
import nju.websoft.chinaopendataportal.Service.MetadataService;
import org.apache.commons.text.similarity.LevenshteinDistance;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import java.util.*;

@Repository
public class SimilarityScore {
    private final MetadataService metadataService;
    private final JdbcTemplate jdbcTemplate;
    private final Logger logger = LoggerFactory.getLogger(SimilarityScore.class);

    private List<Metadata> metadataList;
    public SimilarityScore(MetadataService metadataService, JdbcTemplate jdbcTemplate) {
        this.metadataService = metadataService;
        this.jdbcTemplate = jdbcTemplate;
    }

    public void getSimScoreMatrix() {
        metadataList = metadataService.getAll();

        List<Integer> dataset1IdList = jdbcTemplate.queryForList("SELECT DISTINCT(dataset_id) FROM metadata WHERE dataset_id NOT IN (SELECT DISTINCT(dataset1) FROM simscore)", Integer.class);
        List<Integer> datasetIdList = jdbcTemplate.queryForList("SELECT DISTINCT(dataset_id) FROM metadata ORDER BY dataset_id", Integer.class);

//        ExecutorService pool = Executors.newFixedThreadPool(20);
        for (int dataset_id1 : dataset1IdList) {
            List<Object[]> list = new ArrayList<>();
            for (int dataset_id2 : datasetIdList) {
                if (dataset_id1 >= dataset_id2) continue;
                double simScore = getSim2Score(dataset_id1, dataset_id2);
                Object[] object = new Object[]{dataset_id1, dataset_id2, simScore};
                list.add(object);
//                final int ds1 = dataset_id1;
//                final int ds2 = dataset_id2;
//                final List<Object[]> sim_list = list;
                // 重写runnable对象中的run方法
//                Runnable runnable = () -> {
//                    double simScore = getSim2Score(ds1, ds2);
//                    Object[] object = new Object[]{ds1, ds2, simScore};
//                    sim_list.add(object);
//                };
//                pool.execute(runnable);
            }
            jdbcTemplate.batchUpdate("INSERT INTO simscore VALUES (?,?,?)", list);
            logger.info("dataset id: " + dataset_id1 + ", length: " + list.size());
        }
        logger.info("Completed.");
//        pool.shutdown();
    }

    public double getSim2Score(int dataset1, int dataset2) {
        LevenshteinDistance distance = new LevenshteinDistance();
        double metaSim = 0;
//        Metadata d1 = metadataList.get(dataset1 - 1);
//        Metadata d2 = metadataList.get(dataset2 - 1);
        Metadata d1 = metadataService.getMetadataByDatasetId(dataset1);
        Metadata d2 = metadataService.getMetadataByDatasetId(dataset2);

        /// title
        String title1 = d1.getTitle() != null ? d1.getTitle().trim() :  "" ;
        String title2 = d2.getTitle() != null ? d2.getTitle().trim() :  "" ;
        if (title1.equals(title2)) {
            metaSim += 0.3;
        } else {
            metaSim += 0.3 * (1 - ((double) distance.apply(title1, title2)) / ((double) Math.max(title1.length(), title2.length())));
        }
        // desc
        String desc1 = d1.getDescription() != null ? d1.getDescription().trim() :  "" ;
        String desc2 = d2.getDescription() != null ? d2.getDescription().trim() :  "" ;
        if (desc1.equals(desc2)) {
            metaSim += 0.3;
        } else {
            metaSim += 0.3 * (1 - ((double) distance.apply(desc1, desc2)) / ((double) Math.max(desc1.length(), desc2.length())));
        }
        // province_city_department
        String province1 = d1.getProvince().trim();
        String province2 = d2.getProvince().trim();
        String city1 = d1.getCity().trim();
        String city2 = d2.getCity().trim();
        String department1 = d1.getDepartment() != null ? d1.getDepartment().trim() :  "" ;
        String department2 = d2.getDepartment() != null ? d2.getDepartment().trim() :  "" ;
        if (province1.equals(province2) && city1.equals(city2) && department1.equals(department2)) {
            metaSim += 0.2;
        }
        // url
        String url1 = d1.getUrl() != null ? d1.getUrl().trim() :  "" ;
        String url2 = d2.getUrl() != null ? d2.getUrl().trim() :  "" ;
        if (url1.equals(url2)) {
            metaSim += 0.1;
        }

        // industry
        String industry1 = d1.getStandard_industry() != null ? d1.getStandard_industry().trim() :  "" ;
        String industry2 = d2.getStandard_industry() != null ? d2.getStandard_industry().trim() :  "" ;
        if (industry1.equals(industry2)) {
            metaSim += 0.1;
        }

//        System.out.println(metaSim);
        return metaSim;
    }
}
