def try_handle(func, max_try:int = 3, **args):
	try:
		return func(**args)
	except Exception as e:
		if max_try > 0:
			return try_handle(func, max_try=max_try -1, **args )
		else:
			raise e