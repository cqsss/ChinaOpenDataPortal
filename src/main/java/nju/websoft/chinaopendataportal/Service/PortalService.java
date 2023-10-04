package nju.websoft.chinaopendataportal.Service;

import nju.websoft.chinaopendataportal.Bean.Portal;
import nju.websoft.chinaopendataportal.Mapper.PortalMapper;
import org.springframework.stereotype.Service;

@Service
public class PortalService {
    private final PortalMapper portalMapper;

    public PortalService(PortalMapper portalMapper) {
        this.portalMapper = portalMapper;
    }

    public Portal getPortalByProvinceAndCity(String province, String city) {
        return portalMapper.getPortalByProvinceAndCity(province, city);
    }
}
