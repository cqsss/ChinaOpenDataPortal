package nju.websoft.chinaopendataportal.Ranking;

import java.io.IOException;
import java.util.List;
import java.util.Map;

import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.FieldType;
import org.apache.lucene.index.IndexOptions;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import nju.websoft.chinaopendataportal.GlobalVariances;

@Repository
public class DBIndexer {

    private final JdbcTemplate jdbcTemplate;

    private final Logger logger = LoggerFactory.getLogger(DBIndexer.class);
    private final IndexFactory indexFactory = new IndexFactory();

    public DBIndexer(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    private void generateDocument() throws IOException {
        int datasetCount = 0;
        List<Map<String, Object>> queryList;
        List<Integer> datasetIdList;

        FieldType fieldType = new FieldType();
        fieldType.setStored(true);
        fieldType.setTokenized(true);
        fieldType.setStoreTermVectors(true);
        fieldType.setStoreTermVectorPositions(true);
        fieldType.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS);

        datasetIdList = jdbcTemplate.queryForList("SELECT DISTINCT(dataset_id) FROM metadata", Integer.class);
        //System.out.println(datasetIdList);

        int totalCount = datasetIdList.size();
        logger.info("Start generating document, total: " + totalCount);

        queryList = jdbcTemplate.queryForList("SELECT * FROM metadata ORDER BY dataset_id");

        for (Map<String, Object> di : queryList) {
            Document document = new Document();
            for (Map.Entry<String, Object> entry : di.entrySet()) {
                String name = entry.getKey();
                String value = "";
                if (entry.getValue() != null)
                    value = entry.getValue().toString();
                if (name.equals("category") || name.equals("industry") || name.equals("data_formats") || name.equals("standard_industry")) {
                    String[] tags = value.split(",");
                    for (String si : tags) {
                        document.add(new Field(name, si, fieldType));
                    }
                } else {
                    document.add(new Field(name, value, fieldType));
                }
            }
            datasetCount++;
            // commit document
            indexFactory.commitDocument(document);
            if (datasetCount % 1000 == 0) {
                logger.info("Generated documents: " + datasetCount + "/" + totalCount);
            }
        }
        logger.info("Completed generating document, total: " + datasetCount);
    }

    public void main() throws IOException {
        logger.info("Start.");
        indexFactory.init(GlobalVariances.store_Dir, GlobalVariances.globalAnalyzer);
        generateDocument();
        indexFactory.closeIndexWriter();
        logger.info("Completed.");
    }
}
