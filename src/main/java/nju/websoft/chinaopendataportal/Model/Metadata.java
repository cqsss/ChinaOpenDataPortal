package nju.websoft.chinaopendataportal.Model;

import lombok.Getter;
import lombok.Setter;
import lombok.experimental.Accessors;

@Accessors(fluent = true)
@Getter
@Setter
public class Metadata {
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
