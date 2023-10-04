package nju.websoft.chinaopendataportal.Bean;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class Metadata {
    private long datasetId;
    private String title;
    private String description;
    private String tags;
    private String department;
    private String category;
    private String publish_time;
    private String update_time;
    private String is_open;
    private String data_volume;
    private String industry;
    private String update_frequency;
    private String telephone;
    private String email;
    private String data_formats;
    private String url;
    private String province;
    private String city;
    private String standard_industry;
}
