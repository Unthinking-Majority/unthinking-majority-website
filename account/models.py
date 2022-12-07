from django.db import models


class Account(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=256, help_text='In game name.', unique=True)

    def __str__(self):
        return self.name


class PetOwnership(models.Model):
    account = models.ForeignKey('account.Account', on_delete=models.CASCADE, related_name='pets')
    pet = models.ForeignKey('main.Pet', on_delete=models.CASCADE, related_name='owned_by')
    date = models.DateField(auto_now_add=True)
    proof = models.ImageField(upload_to='account/pet/proof/')

    def __str__(self):
        return self.pet.name
