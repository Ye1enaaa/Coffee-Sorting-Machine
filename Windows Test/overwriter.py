from flask import Flask, request, jsonify
import os
import json
app = Flask(__name__)
@app.route('/update_json', methods=['POST'])
def updateJson():
	try:
		json_data = request.get_json()
		desktop_path = '/home/beancoders/Desktop'
		json_file_path = os.path.join(desktop_path, 'bean.json')
		
		with open(json_file_path,'r') as json_file:
			existing_data = json.load(json_file)
		existing_data['_default']['1']['data']['machineId'] = json_data.get('machineId', existing_data['_default']['1']['data']['machineId'])
		existing_data['_default']['1']['data']['customerId'] = json_data.get('customerId', existing_data['_default']['1']['data']['customerId'])
		existing_data['_default']['1']['data']['bad'] = json_data.get('bad', existing_data['_default']['1']['data']['bad'])
		
		with open(json_file_path,'w') as json_file:
			json.dump(existing_data, json_file, indent=2)
		
		response = {'status':'Success', 'message':'File Updated'}
		
	except Exception as e:
		response = {'status':'error','message':str(e)}
	
	return jsonify(response)
if __name__ == '__main__':
	app.run(debug=True,host='0.0.0.0')




#----------------------------------------------------------------------------------#
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import requests
app = Flask(__name__)
def getPayloadValues():
	path = '/home/beancoders/Desktop'
	jsonFilePath = os.path.join(path,'bean.json')
	
	with open(jsonFilePath,'r') as json_file:
		data = json.load(json_file)
	default_data = data.get('_default',{}).get('1',{}).get('data',{})
	statusId = default_data.get('statusId')
	badCount = default_data.get('bad')
	
	return statusId, badCount

CORS(app)
@app.route('/update_json', methods=['POST'])
def updateJson():
	try:
		json_data = request.get_json()
		desktop_path = '/home/beancoders/Desktop'
		json_file_path = os.path.join(desktop_path, 'bean.json')
		
		with open(json_file_path,'r') as json_file:
			existing_data = json.load(json_file)
		existing_data['_default']['1']['data']['machineId'] = json_data.get('machineId', existing_data['_default']['1']['data']['machineId'])
		existing_data['_default']['1']['data']['statusId'] = json_data.get('statusId', existing_data['_default']['1']['data']['statusId'])
		existing_data['_default']['1']['data']['customerId'] = json_data.get('customerId', existing_data['_default']['1']['data']['customerId'])
		existing_data['_default']['1']['data']['bad'] = json_data.get('bad', existing_data['_default']['1']['data']['bad'])
		
		with open(json_file_path,'w') as json_file:
			json.dump(existing_data, json_file, indent=2)
		
		response = {'status':'Success', 'message':'File Updated'}
		
	except Exception as e:
		response = {'status':'error','message':str(e)}
	
	return jsonify(response)
	
@app.route('/insert-data', methods=['POST'])
def insertData():
	try:
		statusId, badCount = getPayloadValues()
		laravelApiUrl = 'http://192.168.254.111:8000/api/insert-data'
		payload = {
			'statusId': statusId,
			'bad': badCount
		}
		response = requests.post(laravelApiUrl,json=payload)
		if response.status_code == 200:
			return jsonify({'status':'Success'})
		else:
			return jsonify({'status':'Error'})
	except Exception as e:
		response = {'status':'error','message':str(e)}
	
	return jsonify(response)
if __name__ == '__main__':
	app.run(debug=True,host='0.0.0.0')
	

	
