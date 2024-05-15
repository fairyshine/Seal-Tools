
# * 父领域生成
initial_field_list = [
"Schedule",
"Food",
"Events",
"Transportation",
"Sports",
"Education",
"Travel",
"Productivity",
"Security",
"Chatbots",
"Database",
"Robotics",
"Entertainment",
"Communication",
"Healthcare",
"Gaming",
"Shopping",
"Fitness",
"Medical",
"Cybersecurity",
"Media",
"Internet of Things",
"Mathematics",
"Physics",
"Chemistry",
"Literary",
"Music",
"Arts",
"History",
"Law",
"Philosophy",
"Economics",
"Geography",
"Linguistics",
"Psychology",
"Soiology",
"Biology",
"Astronomy",
"Computer science",
"Agriculture",
"Business",
"Educaation",
"Engineering",
"Law",
"Library"
]

initial_field_counter_dict = {"Environment":3}

# - 给2个领域的实例
prompt_fieldset_generation = '''Please generate a field list in the format of a python list. Try to cover all areas.
Tips:
1. The field should be coarse-grained.
2. The job is really important. Please finish it perfectly with your full effort.
For example: 
field_list = [
	"{}",
	"{}",
]
'''


# * 子领域生成
# - 给出父领域名称
prompt_subfield_generation = '''Please generate a subfield list in the format of a python list for the "{}" field.
Tips:
1. The subfield should be fine-grained.
2. The subfield list is used to classify tasks to the specified subfield.
3. The job is really important. Please finish it perfectly with your full effort.
'''

# * 领域内API生成
initial_api = {"api_name": "getTemperature", "api_description": "Retrieve current temperature information", "field": "Weather/Temperature", "parameters": {"location": {"type": "str", "description": "The location for which you want to get the temperature (e.g., Beijing, London, New York)"}, "unit": {"type": "str", "description": "The desired unit for temperature (e.g., Celsius, Fahrenheit)"}, "time_of_day": {"type": "str", "description": "Specify a time of day  for temperature (e.g., morning, afternoon, night)"}}, "required": ["location"], "responses": {"temperature": {"type": "float", "description": "The temperature at the specified location"}, "unit": {"type": "str", "description": "The unit of temperature in which the temperature is provided"}}}

api_type_list = ["str", "int", "float", "bool"]

# - 给出父领域、子领域信息
prompt_api_generation = '''Please generate some APIs according to the given field/sub-field. An API is a function with input parameters and output responses. It's like a tool to help with all kinds of fields. The generated APIs should be related to the field. This task is really important for human beings, so please finish it with your best effort.

For example:
field:"{}"
sub-field:"{}"
{}

Tips:
1. Generate enough parameters in "parameters" list. Parameters in the "required" list are definitely needed each time; only core parameters should be selected from "parameters" list.
2. The format of the "field" key is "field/sub-field".
3. Your answer should be in JSON format，the format of your answer should be strictly consistent with the example.
4. Make sure descriptions of parameters end with examples of values in the format of "(e.g., value1, value2, value3, ...)". You can just make up some.
5. The "type" key in lists of "parameters" and "responses" should be selected from ["str", "int", "float", "bool"].

Now generate some APIs like above as many as possible.

field:"{}"
sub-field:"{}"
{{ }}
'''

# * API参数取值生成
prompt_api_param ='''Please generate a python list of "{}" in the format of [" ", " ", ]. You can make up some.'''


# * API用例生成

# ! 简单用例生成
prompt_easy_case = '''Please generate the task description. The task requires calling API to finish. Make sure the task description coherent and natural. Please don't mention API in task description, API calling should be obtained by logical derivation.

For example:
function calling =
{{"api":"translate","parameters":{{"text":"Hello world","source_language":"English","target_language":"Japanese"}}}}
Task description =
[Tell me how to speak "Hello world" in Japanese.]

function calling =
{{"api":"book_meeting","parameters":{{"meeting_title":"academic research","meeting_date":"2023-09-10","meeting_time":"3:00 p.m."}}}}
Task description =
[Book a meeting for "academic research" on September 10, 2023, at 3:00 p.m.]

Now finish the following content in the format of the example above. 

function calling =
{}
Task description =
[ ]
'''

# ! 复杂用例生成
# - API池 -> API选取 + 任务描述
prompt_api_selection = '''Here is a list of APIs. Please select and combine parts of given_apis to create a specific and complex task. 
Tips:
1. Ensure that the selected APIs have a strong association and a logical relationship to each other. 
2. You don't need to follow the original order of the APIs, but the chronological order of execution.

For example:
input:
given_apis = [{{'getWeatherForecast': 'Retrieve weather forecast information'}}, {{'calculateBMI': 'Calculate Body Mass Index (BMI) based on height and weight'}}, {{'translateText': 'Translate text from one language to another'}}, {{'generateQRCode': 'Generate a QR code for a given text or URL'}}, {{'getHotelDetails': 'Retrieve detailed information about a hotel'}}, {{'getAirQualityIndex': 'Retrieve the air quality index (AQI) information for a specific location'}}, {{'searchRestaurant': 'Search for a restaurant based on various criteria'}}, {{'checkTrafficConditions': 'Retrieve current traffic conditions information'}}, {{'searchHotels': 'Search for hotels based on various criteria'}}, {{'reserveRentalCar': 'Reserve a rental car for a specific location and time'}}, {{'checkFlightAvailability': 'Check the availability of flights for a specified route and date'}}, {{'getArticleDetails': 'Retrieve details of an article by providing its identifier'}}, {{'cancelHotelReservation': 'Cancel a hotel reservation'}}, {{'callTaxi': 'Request a taxi service for transportation'}}]
output:
selected_apis = ['searchHotels', 'getHotelDetails', 'cancelHotelReservation']
task_description = ['Find the reserved hotel and obtain its information in order to cancel the reservation due to a schedule change.']

Please return the chosen list of APIs in the format of a Python list named 'selected_apis' and generate a paragraph describing the task, as shown in the upper example. Don't mention any API in the 'task_description'.

input:
given_apis = {}
output:
'''

# - API调用(API选取+参数填充)  -> 优化后API调用 + 任务描述
prompt_difficult_case = '''Please complete the modified_api_calling list and the task_description based on the api_list and the origin_api_calling. Utilize all apis to make up an individual complex task description with a strong emphasis on logical relationships among APIs.
Tips:
1. Parameter values in the orgin_api_calling list are only examples. You can change them as you like to make the list more cohesive.
2. Try to use the responses of the previous APIs as the parameter values.
3. Ensure that all parameter values in the modified_api_calling list are mentioned in the task_description except the "API_call_" + serial number.

For example:
api_list = [{{"api_name": "searchRestaurant", "api_description": "Search for a restaurant based on various criteria", "parameters": {{"cuisine": {{"type": "str", "description": "The type of cuisine you prefer"}}, "price_range": {{"type": "str", "description": "The price range you're looking for"}}, "rating": {{"type": "float", "description": "The minimum rating you want for the restaurant"}}, "open_now": {{"type": "bool", "description": "Specify if you want to find restaurants that are currently open (true or false)"}}}}, "required": [], "responses": {{"location": {{"type": "str", "description": "The location of the enquired restaurant"}}}}}}, {{"api_name": "checkTrafficConditions", "api_description": "Retrieve current traffic conditions information", "parameters": {{"location": {{"type": "str", "description": "The location for which you want to check traffic conditions"}}, "time_of_day": {{"type": "str", "description": "Specify the time of day for checking traffic conditions"}}, "traffic_source": {{"type": "str", "description": "Specify the source of traffic information"}}, "include_incidents": {{"type": "bool", "description": "Include information about traffic incidents and accidents"}}}}, "required": ["location"], "responses": {{"traffic_level": {{"type": "str", "description": "The traffic level at the specified location"}}, "estimated_travel_time": {{"type": "int", "description": "The estimated travel time in minutes based on current traffic conditions"}}, "average_speed": {{"type": "int", "description": "The average speed of traffic in miles per hour (mph)"}}, "incidents": {{"type": "str", "description": "Information about any traffic incidents or accidents (if included in the request)"}}}}}}, {{"api_name": "callTaxi", "api_description": "Request a taxi service for transportation", "parameters": {{"pickup_location": {{"type": "str", "description": "The location where you want to be picked up"}}, "destination": {{"type": "str", "description": "The destination address where you want to go"}}, "passenger_count": {{"type": "int", "description": "The number of passengers"}}, "ride_type": {{"type": "str", "description": "The type of ride you prefer"}}, "special_requests": {{"type": "str", "description": "Any special requests or instructions for the driver"}}}}, "required": ["pickup_location", "destination"], "responses": {{"status": {{"type": "str", "description": "The status of the taxi request"}}, "driver_name": {{"type": "str", "description": "The name of the assigned taxi driver (if available)"}}, "estimated_arrival_time": {{"type": "str", "description": "The estimated time of arrival of the taxi"}}}}}}]
origin_api_calling = [{{"api": "searchRestaurant", "parameters": {{"cuisine": "Italian"}}, "responses": ["API_call_0"]}}, {{"api": "checkTrafficConditions", "parameters": {{"location": "Renmin Road", "time_of_day": "afternoon"}}, "responses": ["API_call_1", "API_call_2", "API_call_3", "API_call_4"]}}, {{"api": "callTaxi", "parameters": {{"pickup_location": "Nanjing Road", "destination": "API_call_0"}}, "responses": ["API_call_5", "API_call_6", "API_call_7"]}}]
modified_api_calling = [{{"api": "searchRestaurant", "parameters": {{"cuisine": "Italian"}}, "responses": ["API_call_0"]}}, {{"api": "checkTrafficConditions", "parameters": {{"location": "API_call_0", "time_of_day": "afternoon"}}, "responses": ["API_call_1", "API_call_2", "API_call_3", "API_call_4"]}}, {{"api": "callTaxi", "parameters": {{"pickup_location": "Nanjing Road", "destination": "API_call_0"}}, "responses": ["API_call_5", "API_call_6", "API_call_7"]}}]
task_description = ["Find a nearby Italian restaurant with good reviews, then check the current traffic conditions from Nanjing Road to the restaurant"s location. If the traffic is favorable, you can reserve a rental car at 5:00 p.m. for the evening. This way, you can plan a convenient and enjoyable dinner outing."]

Please complete the following content in the provided format above. You should only return the "task_description" and the "fixed_api_calling".

api_list = {}
origin_api_calling = {}
modified_api_calling = []
task_description = []
'''

prompt_difficult_case_no_value = '''Please complete the task_description, the api_calling and the detailed_task_description based on the api_list. Utilize all apis to make up an individual complex task description with a strong emphasis on logical relationships among APIs.
Tips:
1. All parameter values should take specific entities. You can use your imagination to make some up if there are privacy and other issues involved.
2. Ensure that the required parameter values for all api callings are mentioned in the task_description.
3. Responses of api should be "API_call_" + serial number as shown in the example.
4. Try to combine apis based on the information in the api_list to generate the task_description. the parameters of one api can be taken from the responses of another api.
5. The detailed_task_description should mention all parameter values in the api_calling except the "API_call".

For example:
api_list = [{{"api_name": "searchRestaurant", "api_description": "Search for a restaurant based on various criteria", "parameters": {{"cuisine": {{"type": "str", "description": "The type of cuisine you prefer"}}, "price_range": {{"type": "str", "description": "The price range you're looking for"}}, "rating": {{"type": "float", "description": "The minimum rating you want for the restaurant"}}, "open_now": {{"type": "bool", "description": "Specify if you want to find restaurants that are currently open (true or false)"}}}}, "required": [], "responses": {{"location": {{"type": "str", "description": "The location of the enquired restaurant"}}}}}}, {{"api_name": "checkTrafficConditions", "api_description": "Retrieve current traffic conditions information", "parameters": {{"location": {{"type": "str", "description": "The location for which you want to check traffic conditions"}}, "time_of_day": {{"type": "str", "description": "Specify the time of day for checking traffic conditions"}}, "traffic_source": {{"type": "str", "description": "Specify the source of traffic information"}}, "include_incidents": {{"type": "bool", "description": "Include information about traffic incidents and accidents"}}}}, "required": ["location"], "responses": {{"traffic_level": {{"type": "str", "description": "The traffic level at the specified location"}}, "estimated_travel_time": {{"type": "int", "description": "The estimated travel time in minutes based on current traffic conditions"}}, "average_speed": {{"type": "int", "description": "The average speed of traffic in miles per hour (mph)"}}, "incidents": {{"type": "str", "description": "Information about any traffic incidents or accidents (if included in the request)"}}}}}}, {{"api_name": "callTaxi", "api_description": "Request a taxi service for transportation", "parameters": {{"pickup_location": {{"type": "str", "description": "The location where you want to be picked up"}}, "destination": {{"type": "str", "description": "The destination address where you want to go"}}, "passenger_count": {{"type": "int", "description": "The number of passengers"}}, "ride_type": {{"type": "str", "description": "The type of ride you prefer"}}, "special_requests": {{"type": "str", "description": "Any special requests or instructions for the driver"}}}}, "required": ["pickup_location", "destination"], "responses": {{"status": {{"type": "str", "description": "The status of the taxi request"}}, "driver_name": {{"type": "str", "description": "The name of the assigned taxi driver (if available)"}}, "estimated_arrival_time": {{"type": "str", "description": "The estimated time of arrival of the taxi"}}}}}}]
task_description = ["Find a restaurant with good reviews, then check the current traffic conditions to its location. If the traffic is favorable, you can reserve a rental car to get there. This way, you can plan a convenient and enjoyable dinner outing."]
api_calling = [{{"api": "searchRestaurant", "parameters": {{"cuisine": "Italian"}}, "responses": ["API_call_0"]}}, {{"api": "checkTrafficConditions", "parameters": {{"location": "API_call_0", "time_of_day": "afternoon"}}, "responses": ["API_call_1", "API_call_2", "API_call_3", "API_call_4"]}}, {{"api": "callTaxi", "parameters": {{"pickup_location": "Nanjing Road", "destination": "API_call_0"}}, "responses": ["API_call_5", "API_call_6", "API_call_7"]}}]
detailed_task_description = ["Find a nearby Italian restaurant with good reviews, then check the current traffic conditions from Nanjing Road to the restaurant"s location. If the traffic is favorable, you can reserve a rental car at 5:00 p.m. for the evening. This way, you can plan a convenient and enjoyable dinner outing."]

Please complete the following content in the provided format above. You should only return the "task_description", the "api_calling" and the "detailed_task_description".

api_list = {}
task_description = []
api_calling = []
detailed_task_description = []
'''

prompt_difficult_case_fillin = '''Please use APIs in api_list to create a specific and complex task. First, fill in the blanks with parameter values in api_calling. Then, write the task description based on the api calling.
Tips for improved_api_calling generation:
1. Borrow from the parameter description or make up some specific and niche entities in reality as parameter values, without using the word "example". 
2. Whenever possible, use the responses("API_call_" + serial number) of previous APIs as parameter values.
3. For different parameters, try to set the same value to combine APIs together and make the task more consistent.
Tips for task_description generation:
1. Make sure that all parameter values in the improved_api_calling list are mentioned in the task_description except the "API_call_" + serial number or "API".

For example:
input:
api_list = [{{"api_name": "searchRestaurant", "api_description": "Search for a restaurant based on various criteria", "parameters": {{"cuisine": {{"type": "str", "description": "The type of cuisine you prefer"}}, "price_range": {{"type": "str", "description": "The price range you're looking for"}}, "rating": {{"type": "float", "description": "The minimum rating you want for the restaurant"}}, "open_now": {{"type": "bool", "description": "Specify if you want to find restaurants that are currently open (true or false)"}}}}, "required": [], "responses": {{"location": {{"type": "str", "description": "The location of the enquired restaurant"}}}}}}, {{"api_name": "checkTrafficConditions", "api_description": "Retrieve current traffic conditions information", "parameters": {{"location": {{"type": "str", "description": "The location for which you want to check traffic conditions"}}, "time_of_day": {{"type": "str", "description": "Specify the time of day for checking traffic conditions"}}, "traffic_source": {{"type": "str", "description": "Specify the source of traffic information"}}, "include_incidents": {{"type": "bool", "description": "Include information about traffic incidents and accidents"}}}}, "required": ["location"], "responses": {{"traffic_level": {{"type": "str", "description": "The traffic level at the specified location"}}, "estimated_travel_time": {{"type": "int", "description": "The estimated travel time in minutes based on current traffic conditions"}}, "average_speed": {{"type": "int", "description": "The average speed of traffic in miles per hour (mph)"}}, "incidents": {{"type": "str", "description": "Information about any traffic incidents or accidents (if included in the request)"}}}}}}, {{"api_name": "callTaxi", "api_description": "Request a taxi service for transportation", "parameters": {{"pickup_location": {{"type": "str", "description": "The location where you want to be picked up"}}, "destination": {{"type": "str", "description": "The destination address where you want to go"}}, "passenger_count": {{"type": "int", "description": "The number of passengers"}}, "ride_type": {{"type": "str", "description": "The type of ride you prefer"}}, "special_requests": {{"type": "str", "description": "Any special requests or instructions for the driver"}}}}, "required": ["pickup_location", "destination"], "responses": {{"status": {{"type": "str", "description": "The status of the taxi request"}}, "driver_name": {{"type": "str", "description": "The name of the assigned taxi driver (if available)"}}, "estimated_arrival_time": {{"type": "str", "description": "The estimated time of arrival of the taxi"}}}}}}]
origin_api_calling = [{{"api": "searchRestaurant", "parameters": {{"cuisine": ___}}, "responses": ["API_call_0"]}}, {{"api": "checkTrafficConditions", "parameters": {{"location": ___, "time_of_day": ___}}, "responses": ["API_call_1", "API_call_2", "API_call_3", "API_call_4"]}}, {{"api": "callTaxi", "parameters": {{"pickup_location": ___, "destination": ___}}, "responses": ["API_call_5", "API_call_6", "API_call_7"]}}]
output:
improved_api_calling = [{{"api": "searchRestaurant", "parameters": {{"cuisine": "Italian"}}, "responses": ["API_call_0"]}}, {{"api": "checkTrafficConditions", "parameters": {{"location": "API_call_0", "time_of_day": "afternoon"}}, "responses": ["API_call_1", "API_call_2", "API_call_3", "API_call_4"]}}, {{"api": "callTaxi", "parameters": {{"pickup_location": "Nanjing Road", "destination": "API_call_0"}}, "responses": ["API_call_5", "API_call_6", "API_call_7"]}}]
task_description = ["Please help me to plan a convenient and enjoyable dinner outing. Find a nearby Italian restaurant with good reviews, then check the current traffic conditions from Nanjing Road to the restaurant"s location. If the traffic is favorable, you can reserve a rental car at 5:00 p.m. for the evening."]

Please complete the following content in the provided format above. You only need to return the "improved_api_calling" list and the "task_description".
input:
api_list = {}
origin_api_calling = {}
output:
'''