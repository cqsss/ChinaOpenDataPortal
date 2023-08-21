package nju.websoft.chinaopendataportal.Mapper;

import nju.websoft.chinaopendataportal.Bean.Query;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

@Mapper
public interface QueryMapper {

    @Select("SELECT * FROM query WHERE query_text=#{queryText}")
    Query getQueryByText(@Param("queryText") String queryText);

}
