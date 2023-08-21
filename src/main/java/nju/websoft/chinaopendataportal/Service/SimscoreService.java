package nju.websoft.chinaopendataportal.Service;

import nju.websoft.chinaopendataportal.Bean.Simscore;
import nju.websoft.chinaopendataportal.Mapper.SimscoreMapper;
import org.apache.ibatis.annotations.Param;
import org.springframework.stereotype.Service;

@Service
public class SimscoreService {
    private final SimscoreMapper simscoreMapper;

    public SimscoreService(SimscoreMapper simscoreMapper) {
        this.simscoreMapper = simscoreMapper;
    }

    public int getSimscoreCount() {
        return simscoreMapper.getSimscoreCount();
    }

    public double getSimscoreByDatasetId(@Param("dataset1") int dataset1, @Param("dataset2") int dataset2) {
        return simscoreMapper.getSimscoreByDatasetId(dataset1, dataset2);
    }
}
