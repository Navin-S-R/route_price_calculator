// Copyright (c) 2023, Aerele and contributors
// For license information, please see license.txt

frappe.ui.form.on('Route Price calculator', {
	refresh: function(frm) {
		if (!frm.doc.__islocal){
			frm.add_custom_button(__('Calculate Route Price'), function() {
				if (!frm.doc.__unsaved){
					frappe.call({
						method: "route_price_calculator.route_price_calculator.doctype.route_price_calculator.route_price_calculator.calculate_route_price",
						args:{
							docname:frm.doc.name
						},
						freeze: true,
						freeze_message:"Calculating route price, please wait...",
						callback: function (res) {
							if (res.message){
								frappe.set_route('Form', 'Route Price',res.message);
							}
						}
					})
				}
			}).addClass("btn-primary");
		}
	}
});
