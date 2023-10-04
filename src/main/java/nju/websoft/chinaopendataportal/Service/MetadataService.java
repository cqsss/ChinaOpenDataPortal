package nju.websoft.chinaopendataportal.Service;

import java.util.List;

import org.springframework.stereotype.Service;

import nju.websoft.chinaopendataportal.Bean.Metadata;
import nju.websoft.chinaopendataportal.Mapper.MetadataMapper;

@Service
public class MetadataService {
    private final MetadataMapper metadataMapper;

    public MetadataService(MetadataMapper metadataMapper) {
        this.metadataMapper = metadataMapper;
    }

    public int getMetadataCount() {
        return metadataMapper.getMetadataCount();
    }

    public List<Metadata> getAll() {
        return metadataMapper.getAll();
    }

    public Metadata getMetadataByDatasetId(int datasetId) {
        return metadataMapper.getMetadataByDatasetId(datasetId);
    }

    public List<String> getProvinces() {
        return metadataMapper.getProvinces();
    }

    public int getProvinceCount() {
        return metadataMapper.getProvinceCount();
    }

    public List<String> getCitiesByProvince(String province) {
        return metadataMapper.getCitiesByProvince(province);
    }

    public int getCityCount() {
        return metadataMapper.getCityCount();
    }

}
