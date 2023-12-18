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
	
