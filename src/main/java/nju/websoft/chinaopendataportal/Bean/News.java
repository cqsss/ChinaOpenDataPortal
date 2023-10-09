package nju.websoft.chinaopendataportal.Bean;

import lombok.Getter;
import lombok.Setter;
import lombok.experimental.Accessors;

@Accessors(fluent = true)
@Getter
@Setter
public class News {
    String title;
    String detail;
    String date;
}
