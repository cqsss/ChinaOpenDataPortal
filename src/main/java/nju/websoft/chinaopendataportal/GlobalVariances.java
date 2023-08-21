package nju.websoft.chinaopendataportal;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.CharArraySet;
import org.apache.lucene.analysis.cn.smart.SmartChineseAnalyzer;

import java.io.BufferedReader;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.List;

public class GlobalVariances {


//    public static final String index_Dir = "D:\\CQS\\Data\\ChinaOpenDataPortal\\indexes_2023agu";
//    public static String store_Dir = "D:\\CQS\\Data\\ChinaOpenDataPortal\\indexes_2023agu";
    public static String store_Dir = "/home/qschen/Code/ChinaOpenDataPortal/indexes_2023agu";
    public static final String index_Dir = "/home/qschen/Code/ChinaOpenDataPortal/indexes_2023agu";
    public static Analyzer globalAnalyzer = initAnalyzer();
    public static String[] queryFields = {"title", "description", "department", "province", "city", "category", "industry"};
    public static String[] snippetFields = {"department", "is_open", "province", "city", "category", "industry", "data_formats", "publish_time", "update_time"};
    public static String[] filterFields = {"province", "city", "industry", "is_open"};
    public static String[] industryFields = {"全部", "农、林、牧、渔业", "采矿业", "制造业", "电力、热力、燃气及水生产和供应业", "建筑业", "批发和零售业", "交通运输、仓储和邮政业", "住宿和餐饮业", "信息传输、软件和信息技术服务业", "金融业", "房地产业", "租赁和商务服务业", "科学研究和技术服务业", "水利、环境和公共设施管理业", "居民服务、修理和其他服务业", "教育", "卫生和社会工作", "文化、体育和娱乐业", "公共管理、社会保障和社会组织", "国际组织"};
    public static String[] isOpenFields = {"全部", "无条件开放", "有条件开放"};
    public static float[] BoostWeights = {1.0f, 0.6f, 0.5f, 0.8f, 0.8f, 0.2f, 0.2f};
    public static Integer HitSize = 100;
    public static Integer ExperimentSize = 10;

    public static Integer maxCharOfDescription = 500;
    public static int numOfDatasetsPerPage = 10;

    public static Analyzer initAnalyzer() {
        String str;
        List<String> stopWordsList = new ArrayList<>();
        try {
//            FileReader fileReader = new FileReader("D:\\CQS\\Code\\ChinaOpenDataPortal\\src\\main\\resources\\static\\stopwords\\nltk-chinese-stopwords.txt");
            FileReader fileReader = new FileReader("/home/qschen/Code/ChinaOpenDataPortal/nltk-chinese-stopwords.txt");
            BufferedReader bufferedReader = new BufferedReader(fileReader);
            while ((str = bufferedReader.readLine()) != null) {
                stopWordsList.add(str);
            }
            //System.out.println(stopWordsList);
            bufferedReader.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
        CharArraySet cas = new CharArraySet(0, true);
        cas.addAll(stopWordsList);
        return new SmartChineseAnalyzer(cas);
    }
}
