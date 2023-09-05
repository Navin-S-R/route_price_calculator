# Copyright (c) 2023, Aerele and contributors
# For license information, please see license.txt

import frappe
import requests
import json
from frappe.model.document import Document

class RoutePricecalculator(Document):
	pass

@frappe.whitelist()
def calculate_route_price(docname):
	rpc_doc = frappe.get_single("Route Price calculator")
	#From and To locations
	if rpc_doc.determine_location_by == "Geo Location":
		from_location={
			"lat" : rpc_doc.from_address_latitiude,
			"lng" : rpc_doc.from_address_longitude
		}
		to_location = {
			"lat" : rpc_doc.to_address_latitiude,
			"lng" : rpc_doc.to_address_longitude
		}
	elif rpc_doc.determine_location_by == "Address":
		from_location={
			"address" : rpc_doc.from_address
		}
		to_location={
			"address" : rpc_doc.to_address
		}
	elif rpc_doc.determine_location_by == "Place ID":
		from_location = {
			"place_id" : rpc_doc.from_place_id
		}
		to_location = {
			"place_id" : rpc_doc.to_place_id
		}
	# Waypoints
	waypoints=[]
	waypoints_route_price=[]
	for address in rpc_doc.waypoints:
		if address.get("address"):
			waypoints.append({"address": address.get("address")})
			waypoints_route_price.append({"address": address.get("address")})
		elif address.get("latitude") and address.get("longitude"):
			waypoints.append({
				"lat": address.get("latitude"),
				"lng": address.get("longitude")
			})
			waypoints_route_price.append({
				"latitude": address.get("latitude"),
				"longitude": address.get("longitude")
			})
		elif address.get("place_id"):
			waypoints.append({
				"place_id" : address.get("place_id")
			})
			waypoints_route_price.append({
				"place_id" : address.get("place_id")
			})
 
	url = f"{rpc_doc.base_url}/toll/v2/origin-destination-waypoints"
	payload = json.dumps({
		"from": from_location,
		"to": to_location,
		"waypoints": waypoints,
		"vehicleType": rpc_doc.vehicle_type,
		"departure_time": rpc_doc.departure_time,
		"fuelPrice": rpc_doc.fuel_price,
		"fuelPriceCurrency": rpc_doc.fuel_price_currency,
		"fuelEfficiency": {
			"city": rpc_doc.city_mileage,
			"hwy": rpc_doc.highway_mileage,
			"units": rpc_doc.milage_units
		},
		"driver": {
			"wage": rpc_doc.wage,
			"rounding": rpc_doc.rounding,
			"valueOfTime": rpc_doc.value_of_time
		}
	})
	headers = {
	'Content-Type': 'application/json',
	'Accept': 'application/json',
	'x-api-key': rpc_doc.get_password("api_key")
	}
	response = requests.request("POST", url, headers=headers, data=payload).text
	response = json.loads(response)
	if response.get("status") == "OK":
		doc_values={}
		field_list = [
			"determine_location_by",
			"from_address",
			"from_place_id",
			"from_address_latitiude",
			"from_address_longitude",
			"to_address",
			"to_place_id",
			"to_address_latitiude",
			"to_address_longitude",
			"vehicle_type",
			"departure_time",
			"fuel_price",
			"fuel_price_currency",
			"city_mileage",
			"highway_mileage",
			"milage_units",
			"wage",
			"rounding",
			"value_of_time"
		]
		for field in field_list:
			doc_values[field] = rpc_doc.get(field)
		doc_values["doctype"] = "Route Price"
		doc_values["waypoints"] = waypoints_route_price
		route_price_doc = frappe.get_doc(doc_values)
		route_price_doc.insert()
		route_price_doc.route  = json.dumps(response.get("summary").get("route"), indent = 4)
		route_price_doc.summary = json.dumps(response.get("routes")[0].get("summary"), indent = 4)
		route_price_doc.costs = json.dumps(response.get("routes")[0].get("costs"), indent = 4)
		route_price_doc.tolls = json.dumps(response.get("routes")[0].get("tolls"), indent = 4)
		route_price_doc.overall_response = json.dumps(response,indent=4)
		route_price_doc.save()
		return route_price_doc.name
