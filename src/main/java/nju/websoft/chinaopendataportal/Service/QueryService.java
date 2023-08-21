package nju.websoft.chinaopendataportal.Service;

import nju.websoft.chinaopendataportal.Bean.Query;
import nju.websoft.chinaopendataportal.Mapper.QueryMapper;
import org.springframework.stereotype.Service;

@Service
public class QueryService {
    private final QueryMapper queryMapper;

    public QueryService(QueryMapper queryMapper) {
        this.queryMapper = queryMapper;
    }

    public Query getQueryByText(String queryText) {
        return queryMapper.getQueryByText(queryText);
    }

    public boolean findQueryByText(String queryText) {
        return queryMapper.getQueryByText(queryText) != null;
    }

}
