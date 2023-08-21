package nju.websoft.chinaopendataportal.Mapper;

import nju.websoft.chinaopendataportal.Bean.Simscore;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

@Mapper
public interface SimscoreMapper {
    @Select("SELECT COUNT(*) FROM simscore")
    int getSimscoreCount();


    @Select("SELECT simscore FROM simscore WHERE dataset1=#{dataset1} AND dataset2=#{dataset2}")
    double getSimscoreByDatasetId(@Param("dataset1") int dataset1, @Param("dataset2") int dataset2);
}
