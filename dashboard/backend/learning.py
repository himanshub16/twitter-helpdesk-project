import pickle

data = pickle.load(open('./linear_model.sav', 'rb'))

clf = data['model']
tfidf = data['tfidf']
features = data['features']
id_to_topics = data['id_to_topic']


def classify(x):
    if type(x) == str:
        y = clf.predict(tfidf.transform([x]))
        return id_to_topics[y[0]]
    else:
        y = clf.predict(tfidf.transform(x))
        return [id_to_topics[t] for t in y]
