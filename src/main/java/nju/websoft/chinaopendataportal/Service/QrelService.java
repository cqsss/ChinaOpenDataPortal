package nju.websoft.chinaopendataportal.Service;

import nju.websoft.chinaopendataportal.Bean.Qrel;
import nju.websoft.chinaopendataportal.Mapper.QrelMapper;
import org.apache.ibatis.annotations.Param;
import org.springframework.stereotype.Service;

@Service
public class QrelService {
    private final QrelMapper qrelMapper;

    public QrelService(QrelMapper qrelMapper) {
        this.qrelMapper = qrelMapper;
    }

    public Qrel getQrel(int queryId, int datasetId) {
        return qrelMapper.getQrel(queryId, datasetId);
    }

    public boolean findQrel(int queryId, int datasetId) {
        return qrelMapper.getQrel(queryId, datasetId) != null;
    }

    public void insertQrel(int queryId, int datasetId, int relScore) {
        qrelMapper.insertQrel(queryId, datasetId, relScore);
    }
    public void updateRelScoreById(int queryId, int datasetId, int relScore) {
        qrelMapper.updateRelScoreById(queryId, datasetId, relScore);
    }
}
