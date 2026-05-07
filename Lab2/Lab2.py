import os
import weka.core.jvm as jvm
from weka.core.classes import Random
from weka.core.converters import Loader
from weka.classifiers import Classifier, Evaluation, PredictionOutput
from weka.core.dataset import Instance

jvm.start()

# Load dataset
data_file = "air_quality.arff"  # Ensure this file is in the same folder
loader = Loader(classname="weka.core.converters.ArffLoader")
data = loader.load_file(data_file)
data.class_is_last()  # The last attribute is the class (AQI category)

# Split dataset into train/test
train, test = data.train_test_split(66.0, Random(1))  # 66% train, 34% test

# Build and train J48 classifier
cls = Classifier(classname="weka.classifiers.trees.J48")
#cls = Classifier(classname="weka.classifiers.functions.MultilayerPerceptron")

cls.build_classifier(train)

print("=== J48 Classifier Model ===")
print(cls)  # Print the tree structure

# Evaluate the model
output = PredictionOutput(classname="weka.classifiers.evaluation.output.prediction.PlainText")

evl = Evaluation(train)
evl.test_model(cls, test, output=output)

print("\n=== Evaluation Results ===")
print(f"Percent Correct: {evl.percent_correct}%")
print(f"Percent Incorrect: {evl.percent_incorrect}%")
print("Confusion Matrix:")
print(evl.confusion_matrix)

# Predict current air quality for a new instance
# Example AQI values [PM2.5, PM10, O3, NO2, SO2] current_aqi_values = [22, 35, 18, 25, 10]

current_aqi_values_lj = [25,7,3,13,0]
current_aqi_values_bilbao = [17, 9, 18, 13, 3]


inst = Instance.create_instance(current_aqi_values_bilbao) # Change it depending on the city
inst.dataset = data  # Link to dataset structure

predicted_index = int(cls.classify_instance(inst))
predicted_class = inst.class_attribute.value(predicted_index)

print(f"\nPredicted air quality class: {predicted_class}")

jvm.stop()
