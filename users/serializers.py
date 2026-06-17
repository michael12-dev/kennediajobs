from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, label='Confirm password')

    class Meta:
        model = User
        fields = [
            'email', 'username', 'first_name', 'last_name',
            'phone', 'city', 'industry', 'password', 'password2',
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        # Auto-generate username from email if not supplied
        if not validated_data.get('username'):
            validated_data['username'] = validated_data['email'].split('@')[0]
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    application_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'phone', 'city', 'industry', 'years_of_experience', 'linkedin_url',
            'profile_summary', 'cv_file', 'profile_photo', 'current_salary',
            'is_profile_complete', 'role', 'application_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'email', 'role', 'created_at', 'updated_at',
                            'full_name', 'application_count', 'is_profile_complete']

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_application_count(self, obj):
        return obj.applications.count()


class AdminUserSerializer(serializers.ModelSerializer):
    """Serializer for super-admin user management."""
    full_name = serializers.SerializerMethodField()
    application_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'phone', 'city', 'industry', 'is_active',
            'application_count', 'created_at', 'last_login',
        ]
        read_only_fields = ['id', 'created_at', 'last_login']

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_application_count(self, obj):
        return obj.applications.count()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value


class KennediaTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT token with extra user claims."""
    username_field = 'email'

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        # Auto-fix role for superusers created via createsuperuser command
        # (which doesn't know about the custom role field)
        role = user.role
        if user.is_superuser and role not in ('admin', 'super_admin'):
            user.role = 'super_admin'
            user.save(update_fields=['role'])
            role = 'super_admin'
        elif user.is_staff and role not in ('admin', 'super_admin'):
            user.role = 'admin'
            user.save(update_fields=['role'])
            role = 'admin'
        data['user'] = {
            'id': user.id,
            'email': user.email,
            'full_name': user.get_full_name(),
            'role': role,
            'industry': user.industry,
            'is_profile_complete': user.is_profile_complete,
        }
        return data
