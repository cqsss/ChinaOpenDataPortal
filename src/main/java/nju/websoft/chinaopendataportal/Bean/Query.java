package nju.websoft.chinaopendataportal.Bean;


public class Query {

  private long query_id;
  private String query_text;
  private String industry;
  private String province;
  private String city;

  public long getQuery_id() {
    return query_id;
  }

  public void setQuery_id(long query_id) {
    this.query_id = query_id;
  }

  public String getQuery_text() {
    return query_text;
  }

  public void setQuery_text(String query_text) {
    this.query_text = query_text;
  }

  public String getIndustry() {
    return industry;
  }

  public void setIndustry(String industry) {
    this.industry = industry;
  }

  public String getProvince() {
    return province;
  }

  public void setProvince(String province) {
    this.province = province;
  }

  public String getCity() {
    return city;
  }

  public void setCity(String city) {
    this.city = city;
  }
}
