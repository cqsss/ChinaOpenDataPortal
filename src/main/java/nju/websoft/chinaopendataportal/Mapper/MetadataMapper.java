package nju.websoft.chinaopendataportal.Mapper;

import nju.websoft.chinaopendataportal.Bean.Metadata;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

@Mapper
public interface MetadataMapper {

    @Select("SELECT COUNT(*) FROM metadata")
    int getMetadataCount();
    @Select("SELECT * FROM metadata ORDER BY dataset_id")
    List<Metadata> getAll();
    @Select("SELECT * FROM metadata WHERE dataset_id=#{datasetId}")
    Metadata getMetadataByDatasetId(@Param("datasetId") int datasetId);

    @Select("SELECT DISTINCT(province) FROM metadata")
    List<String> getProvinces();

    @Select("SELECT DISTINCT(city) FROM metadata WHERE province=#{province}")
    List<String> getCitiesByProvince(@Param("province") String province);
}
