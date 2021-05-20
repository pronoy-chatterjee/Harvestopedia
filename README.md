## Objective -

Farming is considered a major contributor to a country’s economic growth. In a country like India, it provides bread and butter for a majority of the population. Our country’s population in the next decade is expected to become the largest in the world and with this kind of population explosion, the demand for quantity, quality, and nutritious food is only going to increase. To tackle these issues, we came up with an idea from the field of Precision Farming which is a technology-driven approach to farming that observes, measures, and analyzes the needs of individual fields or crops.

Our primary objective is to provide an Artificial Intelligence-based web application to recommend not only the crops and fertilizers as per the soil information provided by the farmer, but also it will provide the facility to predict any disease the crop has (if any) when an image of the leaf is uploaded. Also, it will suggest some corrective measures to either cure or control the disease.

## Implementation – 

This application has basically 4 parts as follows –
1.	Crop Recommendation – This part of the application recommends which crop is best suited for the farmer depending on various soil parameters like N-P-K (Nitrogen-Phosphorus-Potassium) levels, pH levels, etc. The user needs to input these parameters and then the recommendation will be provided by the machine learning model deployed.
2.	Fertilizer Recommendation - This part of the application recommends which fertilizer is required for the farmer depending on various soil parameters like N-P-K (Nitrogen-Phosphorus-Potassium) levels and the type of crop the farmer is planning to grow. This information when entered by the user gets compared with the ideal values of these parameters for each crop. Any deviation of more than 10 units in these parameters, the application will suggest the corresponding fertilizers. 
3.	Crop Disease Detection - This part of the application needs a leaf image as an input and then detects the type of disease if any the crop is having. It will also provide a little background on the disease and provide some remedies.
4.	Weather Information – This part of the application is a simple API based weather forecasting information display for the farmer’s convenience.

##Future Scope –

1.	In future we are planning to build a mobile application on this concept.
2.	This application in future can be integrated with sensors to detect the soil conditions like N-P-K levels, pH levels of the soil which will make this an Internet of Things use case.
3.	Multiple regional language support like Hindi can be enabled to customize the user’s experience.
4.	In future, we are planning to integrate push notifications via SMS for the farmers if any heavy rainfall or thunderstorm predictions are there.

## Built with - 

1. Programming languages – Python
2. Frameworks - Flask
3. Libraries - Keras, TensorFlow, scikit-learn, numpy, pandas, PIL, pickle
