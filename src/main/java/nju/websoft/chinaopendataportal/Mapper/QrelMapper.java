package nju.websoft.chinaopendataportal.Mapper;

import nju.websoft.chinaopendataportal.Bean.Qrel;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

@Mapper
public interface QrelMapper {
    @Select("SELECT * FROM qrel WHERE query_id=#{queryId} AND dataset_id=#{datasetId}")
    Qrel getQrel(@Param("queryId") int queryId, @Param("datasetId") int datasetId);
    @Update("INSERT INTO qrel VALUES(#{queryId}, #{datasetId}, #{relScore})")
    void insertQrel(@Param("queryId") int queryId, @Param("datasetId") int datasetId, @Param("relScore") int relScore);
    @Update("UPDATE qrel SET rel_score=#{relScore} WHERE query_id=#{queryId} AND dataset_id=#{datasetId}")
    void updateRelScoreById(@Param("queryId") int queryId, @Param("datasetId") int datasetId, @Param("relScore") int relScore);
}
