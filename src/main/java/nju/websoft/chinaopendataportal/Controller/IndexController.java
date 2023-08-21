package nju.websoft.chinaopendataportal.Controller;

import nju.websoft.chinaopendataportal.Ranking.DBIndexer;
import nju.websoft.chinaopendataportal.Ranking.SimilarityScore;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.io.IOException;


@RestController
public class IndexController {
    private final DBIndexer dbIndexer;
    private final SimilarityScore similarityScore;

    public IndexController(DBIndexer dbIndexer, SimilarityScore similarityScore) {
        this.dbIndexer = dbIndexer;
        this.similarityScore = similarityScore;
    }

    @RequestMapping("/index")
    public String DoIndex() throws IOException {
        dbIndexer.main();
        return "success";
    }

    @RequestMapping("/simscore")
    public String DoSimscore() throws IOException {
        similarityScore.getSimScoreMatrix();
        return "success";
    }
}
