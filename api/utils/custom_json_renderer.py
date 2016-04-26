from rest_framework.renderers import JSONRenderer

# class CustomJSONRenderer(JSONRenderer):
# 	#override the render method
# 	def render(self, data, accepted_media_type=None, renderer_context=None):
# 		#call super, as we really just want to mess with the data returned
# 		json_str = super(CustomJSONRenderer, self).render(data, accepted_media_type, renderer_context)
# 		root_element = 'contact'
# 		# import pdb; pdb.set_trace()
# 		#wrap the json string in the desired root element
# 		ret = '{"%s": %s}' % (root_element, json_str)

# 		return ret


class CustomJSONRenderer(JSONRenderer):
    """
        Override the render method of the django rest framework JSONRenderer to allow the following:
        * adding a resource_name root element to all GET requests formatted with JSON
        * reformatting paginated results to the following structure {meta: {}, resource_name: [{},{}]}

        NB: This solution requires a custom pagination serializer and an attribute of 'resource_name'
            defined in the serializer
    """
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response_data = {'error': False, 'data': data}
        try:
            if data.get('code'):
                response_data['error'] = True
                data.pop("code", None)
        except:
            pass
        response = super(CustomJSONRenderer, self).render(response_data, accepted_media_type, renderer_context)

        return response