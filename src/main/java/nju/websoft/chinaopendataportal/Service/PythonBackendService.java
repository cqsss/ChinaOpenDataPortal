package nju.websoft.chinaopendataportal.Service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import com.google.gson.Gson;

import nju.websoft.chinaopendataportal.Model.DTO.QueryHitsDTO;

@Service
public class PythonBackendService {

    @Value("${websoft.chinaopendataportal.python.api}")
    private String pythonBackendUrl;

    private RestTemplate restTemplate = new RestTemplate();
    private Gson gson = new Gson();

    public QueryHitsDTO rerankHits(QueryHitsDTO hits) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<String> entity = new HttpEntity<>(gson.toJson(hits), headers);

        ResponseEntity<String> response = restTemplate.exchange(String.format("%s/rerank", pythonBackendUrl),
                HttpMethod.POST, entity,
                String.class);

        return gson.fromJson(response.getBody(), QueryHitsDTO.class);
    }
}
