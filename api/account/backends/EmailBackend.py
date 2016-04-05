from account.models import ConsumerUser, Employee, AdmUser


class EmailBackend(object):
    def authenticate(self, email=None, password=None):
        # import pdb;pdb.set_trace()
        kwargs = {'email': email}
        try:
            user = ConsumerUser.objects.get(**kwargs)
            if user.check_password(password):
                return user
        except ConsumerUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return ConsumerUser.objects.get(pk=user_id)
        except ConsumerUser.DoesNotExist:
            return None
