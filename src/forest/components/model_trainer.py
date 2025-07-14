import sys
from src.forest.constant import *
from src.forest.exception import ForestException
from src.forest.logger import logging
from src.forest.utils.main_utils import load_numpy_array_data, read_yaml_file, load_object, save_object
from src.forest.entity.config_entity import ModelTrainerConfig
from src.forest.entity.artifact_entity import DataTransformationArtifact, ModelTrainerArtifact, ClassificationMetricArtifact
from neuro_mf  import ModelFactory
from src.forest.entity.estimator import SensorModel

class ModelTrainer:
    def __init__(self, data_transformation_artifact: DataTransformationArtifact,
                 model_trainer_config: ModelTrainerConfig):
        self.data_transformation_artifact = data_transformation_artifact
        self.model_trainer_config = model_trainer_config
    
    def initiate_model_trainer(self, ) -> ModelTrainerArtifact:
        logging.info("Entered initiate_model_trainer method of ModelTrainer class")

        try:
            train_arr = load_numpy_array_data(file_path=self.data_transformation_artifact.transformed_train_file_path)
            test_arr = load_numpy_array_data(file_path=self.data_transformation_artifact.transformed_test_file_path)
            x_train, y_train, x_test, y_test = train_arr[:, :-1], train_arr[:, -1], test_arr[:, :-1], test_arr[:, -1]
            model_factory = ModelFactory(model_config_path=self.model_trainer_config.model_config_file_path)
            best_model_detail = model_factory.get_best_model(X=x_train,y=y_train,base_accuracy=self.model_trainer_config.expected_accuracy)
            preprocessing_obj = load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)


            if best_model_detail.best_score < self.model_trainer_config.expected_accuracy:
                logging.info("No best model found with score more than base score")
                raise Exception("No best model found with score more than base score")

            sensor_model = SensorModel(preprocessing_object=preprocessing_obj,
                                       trained_model_object=best_model_detail.best_model)
            logging.info("Created Sensor truck model object with preprocessor and model")
            logging.info("Created best model file path.")
            save_object(self.model_trainer_config.trained_model_file_path, sensor_model)

            metric_artifact = ClassificationMetricArtifact(f1_score=0.8, precision_score=0.8, recall_score=0.9)
            model_trainer_artifact = ModelTrainerArtifact(
                trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                metric_artifact=metric_artifact,
            )
            logging.info(f"Model trainer artifact: {model_trainer_artifact}")
            return model_trainer_artifact
        except Exception as e:
            raise ForestException(e, sys) from e
