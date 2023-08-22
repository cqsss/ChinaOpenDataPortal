package nju.websoft.chinaopendataportal.Bean;


public class Qrel {

  private long query_id;
  private long dataset_id;
  private long rel_score;

  public long getQuery_id() {
    return query_id;
  }

  public void setQuery_id(long query_id) {
    this.query_id = query_id;
  }

  public long getDataset_id() {
    return dataset_id;
  }

  public void setDataset_id(long dataset_id) {
    this.dataset_id = dataset_id;
  }

  public long getRel_score() {
    return rel_score;
  }

  public void setRel_score(long rel_score) {
    this.rel_score = rel_score;
  }
}
