package nju.websoft.chinaopendataportal.Mapper;

import nju.websoft.chinaopendataportal.Bean.Portal;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

@Mapper
public interface PortalMapper {
    @Select("SELECT * FROM portal WHERE province=#{province} AND city=#{city}")
    Portal getPortalByProvinceAndCity(@Param("province") String province, @Param("city") String city);
}
