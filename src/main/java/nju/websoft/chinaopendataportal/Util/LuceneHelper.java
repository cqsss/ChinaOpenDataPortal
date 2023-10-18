package nju.websoft.chinaopendataportal.Util;

import java.nio.file.Paths;
import java.util.Map;

import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.store.MMapDirectory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class LuceneHelper {
    private IndexReader indexReader = null;
    private IndexSearcher indexSearcher = null;
    private Map<String, String> indexMetadata = null;

    @Autowired
    public LuceneHelper(String indexDir) {
        try {
            DirectoryReader dirReader = DirectoryReader.open(MMapDirectory.open(Paths.get(indexDir)));
            indexReader = dirReader;
            indexMetadata = dirReader.getIndexCommit().getUserData();
            indexSearcher = new IndexSearcher(indexReader);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Bean
    public IndexReader indexReader() {
        return indexReader;
    }

    @Bean
    public IndexSearcher indexSearcher() {
        return indexSearcher;
    }

    @Bean
    public Map<String, String> indexMetadata() {
        return indexMetadata;
    }
}
