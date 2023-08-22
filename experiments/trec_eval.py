import pymysql
import pytrec_eval

methods = ['BM25', 'TFIDF', 'LMD']

measures = ['recall_5', 'recall_10', 'ndcg_cut_5', 'ndcg_cut_10', 'map_cut_5', 'map_cut_10']

db = pymysql.connect(host='114.212.190.189',
                     user='qschen',
                     password='chenqiaosheng123',
                     database='china_open_data_portal_2023jun',
                     charset='utf8')

c = db.cursor()

qrel = {}

print(pytrec_eval.supported_measures)


def get_qrel():
    sql = f"SELECT * FROM qrel"
    c.execute(sql)
    qrels = c.fetchall()
    for qi in qrels:
        qid = str(qi[0])
        dsid = str(qi[1])
        if qid not in qrel:
            qrel[qid] = {}
        qrel[qid][dsid] = int(qi[2])


def cal(method):
    sql = "SELECT * FROM results WHERE method=%s"
    c.execute(sql, method)
    results = c.fetchall()
    run = {}
    for ri in results:
        qid = str(ri[0])
        dsid = str(ri[1])
        if qid not in run:
            run[qid] = {}
        run[qid][dsid] = float(ri[2])
    evaluator = pytrec_eval.RelevanceEvaluator(qrel, measures)
    return evaluator.evaluate(run)


get_qrel()

for method in methods:
    metrics = cal(method)
    mean_metric = {x: 0.0 for x in measures}
    n = 100
    for m in metrics:
        for i in metrics[m]:
            mean_metric[i] += metrics[m][i] / n
    print(method, [x for x in mean_metric.values()])
    for k in range(10, 60, 10):
        metrics = cal(f"{method}+MMR{k}")
        mean_metric = {x: 0.0 for x in measures}
        n = 100
        for m in metrics:
            for i in metrics[m]:
                mean_metric[i] += metrics[m][i] / n
        print(f"{method}+MMR{k}", [x for x in mean_metric.values()])
