from django.contrib.auth.models import User
from rest_framework import serializers

from expenses.models import Profile, BankAccount, ExpensePart, Expense, File, Payment, Comment


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ('name', )
        read_only_fields = ('__all__', )


class ProfileSerializer(serializers.ModelSerializer):
    default_account = BankAccountSerializer()

    class Meta:
        model = Profile
        fields = ('bank_account', 'sorting_number', 'bank_name', 'default_account')


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'profile')
        read_only_fields = ('username', 'first_name', 'last_name')


class ExpensePartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpensePart
        fields = '__all__'
        # fields = ('id', 'expense', 'budget_line_name', 'cost_centre_name',
        #           'committee_name', 'amount', 'attested_by', 'attest_date')
        read_only_fields = ('id', 'attested_by', 'attest_date')


class ExpenseSerializer(serializers.ModelSerializer):
    expensepart_set = ExpensePartSerializer(many=True)
    owner = serializers.SerializerMethodField()
    confirmed_by = UserSerializer()

    def get_owner(self, obj):
        return UserSerializer(obj.owner.user).data

    class Meta:
        model = Expense
        fields = ('id', 'owner', 'created_date', 'expense_date', 'confirmed_by',
                  'confirmed_at', 'description', 'reimbursement', 'verification', 'expensepart_set')
        read_only_fields = ('id', 'owner', 'created_date', 'confirmed_by',
                            'confirmed_at', 'reimbursement', 'verification')


class PaymentSerializer(serializers.ModelSerializer):
    expense_set = ExpenseSerializer(many=True)
    account = BankAccountSerializer()
    payer = serializers.SerializerMethodField()
    receiver = serializers.SerializerMethodField()

    def get_payer(self, obj):
        return UserSerializer(obj.payer.user).data

    def get_receiver(self, obj):
        return UserSerializer(obj.receiver.user).data

    class Meta:
        model = Payment
        fields = ('id', 'date', 'payer', 'receiver', 'account', 'expense_set')
        read_only_fields = ('__all__',)


class FileSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        fields = ['expense', 'invoice']
        linked_to = [field in attrs for field in fields]

        if not any(linked_to):
            raise serializers.ValidationError("File needs to be linked to a model")
        if sum(linked_to) > 1:
            raise serializers.ValidationError("File can't be linked to multiple models")

    class Meta:
        model = File
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    def get_author(self, obj):
        return UserSerializer(obj.author.user).data

    def validate(self, attrs):
        fields = ['expense', 'invoice']
        linked_to = [field in attrs for field in fields]

        if not any(linked_to):
            raise serializers.ValidationError("File needs to be linked to a model")
        if sum(linked_to) > 1:
            raise serializers.ValidationError("File can't be linked to multiple models")

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('expense', 'invoice', 'date', 'author')

