from flask import Flask
from flask_restful import reqparse, Resource, Api, abort
import pickle
import pydantic
from typing import List, Tuple, Dict
import plotly.express as px
import random
import math
import time


RESOURCES = {
    'test': [],
    'validate' : [],
    'train' : []
}

STATISTICS ={
    'initial_distribution_literal_array': [],
    'number_synsets_per_literal_array': [],
    'sorted_distribution_literal_array': [],
    'sorted_number_synsets_per_literal_array': [],
    'literal_number': 0,
    'average_sentences_per_literal': 0,
    'average_synsets_per_literal': 0,
    'minimum_number_of_sentences': 0,
    'word_with_minimum_sentences': '',
    'maximum_number_of_sentences': 0,
    'word_with_maximum_sentences': '',
    'minimum_number_of_synsets': 0,
    'word_with_minimum_synsets': '',
    'maximum_number_of_synsets': 0,
    'word_with_maximum_synsets': '',
    'synsets_distribution_percentage_labels': [],
    'synsets_distribution_percentage_values': [],
    'sentences_over_literals_distribution_percentage_labels': [],
    'sentences_over_literals_distribution_percentage_values': [],
    'train_proportion': 0,
    'test_proportion': 0,
    'validate_proportion': 0,
    'distance_metric': 0,
    'distribution_metric': 0,
    'invalid_sentences_percentage_labels' : [],
    'invalid_sentences_percentage_values': []
}


score_dictionary = {} 

app = Flask(__name__)
api = Api(app)

class LiteralItem(pydantic.BaseModel):
    user_id: str
    literal: str
    synsets: str
    correct_synset_id: str
    text_prefix: str
    text: str
    text_postfix: str
    sentence: str

class Literal(pydantic.BaseModel):
  literal: str
  data: List[LiteralItem] = []

class Dataset(pydantic.BaseModel):
  dataset: str # train, test, validation
  literals: List[Literal] = []

def pydantic_to_dict(dataset: Dataset) -> Dict[str, List[Dict[str,str]]]:
  dataset_dict = {}
  for literal in dataset.literals:
    data_list = []
    for data in literal.data:
      data_list.append(data.dict())
    dataset_dict[literal.literal] = data_list

  return dataset_dict

def clean_dataset(dataset: Dataset) -> Dataset:
  dict_dataset = pydantic_to_dict(dataset)
  
  def dict_to_pydantic_filtered(dataset: Dataset) -> Dataset:
    literals = []
    for key in dict_dataset.keys():
      literal_values = []
      for values in dict_dataset[key]:
        data = LiteralItem(**values)
        if data.correct_synset_id != "-1":
          literal_values.append(data)
      literal = Literal(literal=key, data=literal_values)
      if len(literal.data) != 0:
        literals.append(literal)
    dataset = Dataset(dataset=dataset.dataset, literals=literals)

    return dataset

  dataset = dict_to_pydantic_filtered(dataset)
  return dataset

def metric(train_dataset_clean: Dataset, test_dataset_clean: Dataset, validation_dataset_clean: Dataset):
  def get_sysents_distribution_per_literal(dataset: Dataset) -> Dict[str, int]:
    dict_ = {}
    dict_dataset = pydantic_to_dict(dataset)
    for key in dict_dataset.keys():
      dict_[key] = 0

    for literal in dataset.literals:
      synsets_dict = {}
      synsets_size = len(literal.data[0].synsets.split(" ")) - 2
      for literal_prop in literal.data:
        synsets_dict[literal_prop.correct_synset_id] = 0
      dict_[literal.literal] = len(synsets_dict.keys())/synsets_size
    return dict_


  num_synsets_train = get_sysents_distribution_per_literal(train_dataset_clean)
  num_synsets_test = get_sysents_distribution_per_literal(test_dataset_clean)
  num_synsets_validation = get_sysents_distribution_per_literal(validation_dataset_clean)


  total_sum = 0
  for key in num_synsets_train.keys():
    total_sum += (num_synsets_train[key] + num_synsets_test[key] + num_synsets_validation[key])/3

  STATISTICS['distribution_metric'] = total_sum/len(num_synsets_test.keys())

class DatasetResource:

    dataset : Dataset
    train_dataset : Dataset
    validation_dataset : Dataset
    test_dataset : Dataset
    

    def __init__(self):
        in_file = open("dataset.pickle", "rb")
        dict_dataset = pickle.load(in_file)
        literals = []
        for key in dict_dataset.keys():
            literal_values = []
            for values in dict_dataset[key]:
                data = LiteralItem(**values)
                literal_values.append(data)
            literal = Literal(literal=key, data=literal_values)
            literals.append(literal)
        self.dataset = Dataset(dataset="total", literals=literals)

    def calculate_proportions(self, length: int, x:int, y:int, z:int) -> Tuple[int, int, int]:
        z_len = math.ceil(length*z/100)
        y_len = min(length-z_len, math.ceil(length*y/100))
        x_len = length - z_len - y_len

        return x_len, y_len, z_len

    def split_function(self, x:int, y:int, z:int, activate_graph: bool = True):

        # initialize datasets
        train_dataset = Dataset(dataset="train")
        validation_dataset = Dataset(dataset="validation")
        test_dataset = Dataset(dataset="test")

        # itearate dataset and split in x, y, z in this order of proportions
        literal_array = []
        no_synsets_each_word_array = []
        for literal_data in self.dataset.literals:
            literal_array.append(literal_data.literal)
            no_synsets_each_word_array.append(len(literal_data.data[0].synsets.split(' ')))

        if activate_graph is True:
            fig = px.bar(x=literal_array, y=no_synsets_each_word_array, title="Initial distribution")
            fig.show()

        sorted_literal = [x for _, x in sorted(zip(no_synsets_each_word_array, literal_array), reverse=True)]
        sorted_synsets = [_ for _, x in sorted(zip(no_synsets_each_word_array, literal_array), reverse=True)]

        correct_literals = []
        correct_synsets = []
        unique_synsets = list(set(sorted_synsets))
        unique_synsets.sort(reverse=True)
        for i in unique_synsets:
            current_literals = []
            current_synsets = []
            for j in range(len(sorted_synsets)):
                if sorted_synsets[j] == i:
                    current_literals.append(sorted_literal[j])
                    current_synsets.append(sorted_synsets[j])
            current_literals.sort()
            correct_literals += current_literals
            correct_synsets += current_synsets
            
        if activate_graph is True:
            fig = px.bar(x=correct_literals, y=correct_synsets, title="Sorted descending by no synsets, alphabetically ascending for each synset value")
            fig.show()

        for i in range(len(correct_literals)):
            for literal_value in self.dataset.literals:
                if literal_value.literal == correct_literals[i]:
                    synsets_values = literal_value.data[0].synsets.strip().split(' ')
                    synsets_data_complete = [[] for _ in range(len(synsets_values))]
                    existing_sentences = []
                    for literal_data in literal_value.data:
                        for j in range(len(synsets_values)):
                            if literal_data.correct_synset_id == synsets_values[j] and literal_data.sentence not in existing_sentences:
                                existing_sentences.append(literal_data.sentence)
                                synsets_data_complete[j].append(literal_data)
                                break
                    train_literal = Literal(literal=correct_literals[i])
                    validation_literal = Literal(literal=correct_literals[i])
                    test_literal = Literal(literal=correct_literals[i])
                    for j in synsets_data_complete:
                        if len(j) != 0:
                            random.shuffle(j)
                            x_len, y_len, z_len = self.calculate_proportions(length=len(j), x=x, y=y, z=z)
                            train_literal.data.extend(j[:x_len])
                            validation_literal.data.extend(j[x_len:x_len+y_len])
                            test_literal.data.extend(j[x_len+y_len:])
                    train_dataset.literals.append(train_literal)
                    validation_dataset.literals.append(validation_literal)
                    test_dataset.literals.append(test_literal)
        self.train_dataset = train_dataset
        self.validation_dataset  = validation_dataset
        self.test_dataset = test_dataset

        RESOURCES['test'] = test_dataset
        RESOURCES['train'] = train_dataset
        RESOURCES['validate'] = validation_dataset

        x_, y_, z_ = 0, 0, 0
        for i in train_dataset.literals:
            x_ += len(i.data)
        for i in validation_dataset.literals:
            y_ += len(i.data)
        for i in test_dataset.literals:
            z_ += len(i.data)
        total = 0
        for i in self.dataset.literals:
            total += len(i.data)
        
        train_dataset_clean = clean_dataset(train_dataset)
        test_dataset_clean = clean_dataset(test_dataset)
        validation_dataset_clean = clean_dataset(validation_dataset)
        dataset_clean = clean_dataset(self.dataset)
  
        
        metric(train_dataset_clean=train_dataset_clean, test_dataset_clean=test_dataset_clean, validation_dataset_clean=validation_dataset_clean)
        invalid_percent = len(dataset_clean.literals)*100/len(self.dataset.literals)
        values = [ invalid_percent, 100-invalid_percent ]
        labels = [ "Invalid Literals %", "Valid Literals %" ]

        STATISTICS['initial_distribution_literal_array'] = literal_array
        STATISTICS['number_synsets_per_literal_array'] = no_synsets_each_word_array
        STATISTICS['sorted_distribution_literal_array'] = correct_literals
        STATISTICS['sorted_number_synsets_per_literal_array'] = correct_synsets
        STATISTICS['test_proportion'] = z_*100/total
        STATISTICS['validate_proportion'] = y_*100/total
        STATISTICS['train_proportion'] = x_*100/total
        STATISTICS['distance_metric'] = ((x_*100/total)/x + (y_*100/total)/y + (z_*100/total)/z)/3
        STATISTICS['invalid_sentences_percentage_labels'] = labels
        STATISTICS['invalid_sentences_percentage_values'] = values

        new_key = str(x)+" "+str(y)+" "+str(z)
        if new_key not in score_dictionary:
            score_dictionary[new_key] = STATISTICS['distance_metric']


         
    def generate_statistics(self):

        all_sentences : int  = 0
        all_synsets : int  = 0
        literals_name = []
        sentences_number = []
        synsets_number = []
        dict_number_synsets = {}
        dict_number_sentences = {}
        for literal in self.dataset.literals:
            all_sentences += len(literal.data)
            all_synsets += len(literal.data[0].synsets.split(" "))
            literals_name.append(literal.literal)
            sentences_number.append(len(literal.data))
            synsets_number.append(len(literal.data[0].synsets.split(" ")))
            key = str(len(literal.data[0].synsets.split(" ")))
            if key in dict_number_synsets.keys():
                dict_number_synsets[key] += 1
            else:
                dict_number_synsets[key] = 1
            key1 = str(len(literal.data))
            if key1 in dict_number_sentences.keys():
                dict_number_sentences[key1] += 1
            else:
                dict_number_sentences[key1] = 1
        values = [ (dict_number_synsets[x] * 100)/len(self.dataset.literals) for x in sorted(dict_number_synsets.keys()) ]
        labels = [ f"{x} synsets" for x in sorted(dict_number_synsets.keys()) ]
        values1 = [ (dict_number_sentences[x] * 100)/len(self.dataset.literals) for x in sorted(dict_number_sentences.keys()) ]
        labels1 = [ f"{x} sentences" for x in sorted(dict_number_sentences.keys()) ]
        STATISTICS['literal_number'] = len(self.dataset.literals)
        STATISTICS['average_sentences_per_literal'] = all_sentences/len(self.dataset.literals)
        STATISTICS['average_synsets_per_literal'] = all_synsets/len(self.dataset.literals)
        STATISTICS['minimum_number_of_sentences'] = min(sentences_number)
        STATISTICS['maximum_number_of_sentences'] = max(sentences_number)
        STATISTICS['word_with_minimum_sentences'] = literals_name[sentences_number.index(min(sentences_number))]
        STATISTICS['word_with_maximum_sentences'] = literals_name[sentences_number.index(max(sentences_number))]
        STATISTICS['minimum_number_of_synsets'] = min(synsets_number)
        STATISTICS['maximum_number_of_synsets'] = max(synsets_number)
        STATISTICS['word_with_minimum_synsets'] = literals_name[synsets_number.index(min(synsets_number))]
        STATISTICS['word_with_maximum_synsets'] = literals_name[synsets_number.index(max(synsets_number))]
        STATISTICS['synsets_distribution_percentage_labels'] = labels
        STATISTICS['synsets_distribution_percentage_values'] = values
        STATISTICS['sentences_over_literals_distribution_percentage_labels'] = labels1
        STATISTICS['sentences_over_literals_distribution_percentage_values'] = values1



data_resource=DatasetResource()


parser = reqparse.RequestParser()
parser.add_argument('test_split_value')
parser.add_argument('train_split_value')
parser.add_argument('validate_split_value')


def abort_if_set_doesnt_exist(dataset_name):
    if dataset_name not in RESOURCES:
        abort(404, message="Todo {} doesn't exist".format(dataset_name))

class SplitDataset(Resource):
    def get(self, dataset_name):
        abort_if_set_doesnt_exist(dataset_name)
        return RESOURCES[dataset_name].dict()


class SplitDatasetList(Resource):
    def get(self):
        data_resource.generate_statistics()
        return STATISTICS
    def post(self):
        args = parser.parse_args()
        train_split = int(args['train_split_value'])
        test_split = int(args['test_split_value'])
        validate_split = int(args['validate_split_value'])
        data_resource.split_function(train_split,validate_split,test_split, False)
        return {"response":"Split was successful!", "status":200}


class ScoreResource(Resource):
    def get(self):
        sorted_score = dict(sorted(score_dictionary.items(), key=lambda item: item[1]))
        return sorted_score


api.add_resource(SplitDataset, '/<string:dataset_name>')
api.add_resource(ScoreResource,'/score')
api.add_resource(SplitDatasetList,'/split')
if __name__ == '__main__':
    app.run(debug=True)