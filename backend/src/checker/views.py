from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import File, LintFile
from .serializers import (FileSerializer, FileSerializerWithDepth,
                          LintFileHyperSerializer, LintFileSerializer,
                          UserSerializer)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer
    queryset = User.objects.all()


class FileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = File.objects.all()
    serializer_class = FileSerializer

    @staticmethod
    def create_check_task(request, instance):
        kwargs = {}
        try:
            if linter := request.data.pop("linter", None):
                kwargs["linter"] = linter[0] if isinstance(linter, list) else linter
            kwargs["raw_file"] = instance.pk
        except AttributeError:
            return
        serializer = LintFileSerializer(data=kwargs)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

    @staticmethod
    def edit_request(request):
        try:
            request.data["user_id"] = request.user.id
            request.data["user"] = reverse("user-detail", args=[request.user.id])
            request.data["file_name"] = "test"
            if raw_file := request.data.get("raw_file"):
                request.data["file_name"] = raw_file.name
        except AttributeError:
            return request
        return request

    def destroy(self, request, *args, **kwargs):
        instance: File = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        fields = ["id", "url", "file_name", "raw_file", "last_check", "status", "user"]
        request = self.edit_request(request)
        serializer = self.get_serializer(data=request.data, fields=fields)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        self.create_check_task(request, serializer.instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = FileSerializerWithDepth(
            instance,
            fields=["id", "file_name", "url", "raw_file", "last_check", "status", "checks"],
            context=self.get_serializer_context(),
        )
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        fieds = ["id", "url", "file_name", "raw_file", "last_check", "status", "user"]
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, fields=fieds, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, fields=fieds, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        request = self.edit_request(request)
        instance = self.get_object()
        if instance.user != request.user and not request.user.is_superuser:
            return Response("You can update only your files", status=status.HTTP_403_FORBIDDEN)
        self.create_check_task(request, instance)
        return super(FileViewSet, self).update(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        return File.objects.prefetch_related("checks").filter(user=user, is_deleted=False)

    @action(detail=True, methods=["post"])
    def re_check(self, request, pk):
        pk = int(pk)
        request.data["raw_file"] = pk
        file = get_object_or_404(File, pk=pk)
        if file.user != request.user and not request.user.is_superuser:
            return Response("You re_check only your files", status=status.HTTP_403_FORBIDDEN)
        checks = file.checks.all()
        if checks:
            request.data["linter"] = checks.last().linter
        serializer = LintFileSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(f"Can't find file with pk {pk}, {serializer.errors}", status=status.HTTP_400_BAD_REQUEST)
        lint_file: LintFile = serializer.save()
        return Response({"status": f"Task successfuly created {lint_file=}"})


class LintFileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LintFile.objects.all()
    serializer_class = LintFileHyperSerializer


@api_view(["POST"])
def register_api(request):
    UserModel = get_user_model()
    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")

    user_filter = Q(username=username) | Q(email=email)
    for user in UserModel.objects.filter(user_filter):
        # "for" is for better sql optimization
        if user.email == email:
            return Response(
                {"error_message": "Пользователь с таким email уже существует"}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            return Response(
                {"error_message": "Пользователь с таким username уже существует"}, status=status.HTTP_400_BAD_REQUEST
            )

    user = UserModel.objects.create_user(username=username, email=email, password=password)
    login(request, user)
    return Response({"message": "Регистрация успешно завершена"}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def login_api(request):
    UserModel = get_user_model()
    email = request.data.get("email")
    password = request.data.get("password")
    try:
        user = UserModel.objects.get(email=email)
    except UserModel.DoesNotExist:
        return Response({"error_message": "Неверные логин или пароль"}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        if user.check_password(password):
            login(request, user)
            return Response({"message": "Авторизация успешна"}, status=status.HTTP_200_OK)
    return Response({"error_message": "Неверные логин или пароль"}, status=status.HTTP_401_UNAUTHORIZED)


def register_view(request):
    return render(request, "registration.html")


def login_view(request):
    return render(request, "login.html")


@login_required(login_url="login_view")
def file_detail(request, file_id):
    file = get_object_or_404(File, pk=file_id)
    if file.user != request.user and not request.user.is_superuser:
        return Response("You can see only your files", status=status.HTTP_403_FORBIDDEN)
    if file.is_deleted:
        raise Http404("No matches the given query.")
    return render(request, "file_details.html", context={"file": file})


@login_required(login_url="login_view")
def home_page(request):
    return render(request, "home.html")
