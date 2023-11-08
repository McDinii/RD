from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.crypto import get_random_string
from faker import Faker
from django.db.models import F
from core.models import Node, Employee, Address, Contact, Product

fake = Faker()


class Command(BaseCommand):
    help = 'Fill the database with test data'

    @transaction.atomic
    def handle(self, *args, **options):
        if Node.objects.exists() or Employee.objects.exists() or Product.objects.exists():
            self.stdout.write(self.style.SUCCESS('Data already exists in the database. Skipping filltestdata command.'))
            return
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
            username='admin',
            email='admin@admin.com',
            password='admin',
            )
        factories = [Node.objects.create(name=fake.company(), type='factory', debt=0) for _ in range(3)]
        individuals = []
        big_retail_networks = []
        dealerships = []
        distributors = []

        for factory in factories:
            individuals.append(Node.objects.create(
                name=fake.company(),
                type='individual',
                debt=fake.pydecimal(left_digits=5, right_digits=2, positive=True, max_value=10000),
                parent=factory
            ))

            big_retail_node = Node.objects.create(
                name=fake.company(),
                type='big_retail',
                debt=fake.pydecimal(left_digits=5, right_digits=2, positive=True, max_value=10000),
                parent=factory
            )
            big_retail_networks.append(big_retail_node)

            individual_node = fake.random_element(elements=individuals)
            individual_node.parent = big_retail_node
            individual_node.save()

            dealership_node = Node.objects.create(
                name=fake.company(),
                type='dealer',
                debt=fake.pydecimal(left_digits=5, right_digits=2, positive=True, max_value=10000),
                parent=big_retail_node
            )
            dealerships.append(dealership_node)

            individual_node = fake.random_element(elements=individuals)
            individual_node.parent = dealership_node
            individual_node.save()

            distributor_node = Node.objects.create(
                name=fake.company(),
                type='distributor',
                debt=fake.pydecimal(left_digits=5, right_digits=2, positive=True, max_value=10000),
                parent=dealership_node
            )
            distributors.append(distributor_node)

            individual_node = fake.random_element(elements=individuals)
            individual_node.parent = distributor_node
            individual_node.save()

        all_nodes = nodes = factories + individuals + big_retail_networks + dealerships + distributors

        type_order = ['distributor', 'dealer', 'big_retail', 'individual']
        for node_type in type_order:
            for _ in range(2):
                parent_node = factories if node_type == 'distributor' else [n for n in all_nodes if n.type == 'distributor']
                parent_node = fake.random_element(elements=parent_node)

                new_node = Node.objects.create(
                    name=fake.company(),
                    type=node_type,
                    debt=fake.pydecimal(left_digits=5, right_digits=2, positive=True, max_value=10000),
                    parent=parent_node
                )
                all_nodes.append(new_node)

        for node in all_nodes:
            address = Address.objects.create(
                country=fake.country(),
                city=fake.city(),
                street=fake.street_name(),
                house_number=fake.building_number(),
            )
            contact = Contact.objects.create(
                email=fake.email(),
                address=address,
                node=node,
            )

            user = User.objects.create(
                username=fake.unique.user_name(),
                email=fake.unique.email(),
                password=fake.password(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
            )

            Employee.objects.create(
                user=user,
                first_name=user.first_name,
                last_name=user.last_name,
                active =fake.random_element(elements=(True, False)),
                node_network=node,
            )

            product_names = ['MacBook', 'MacBook Pro', 'MacBook Air', 'iPhone 12', 'iPhone 13', 'iPhone 14', 'iPhone 15',
                             'iPad', 'iPad 13.9', 'AirPods', 'Apple Watch', 'iMac', 'Mac mini']
            product_modeles = ['Pro', 'Pro Max', 'Air', '2020', '2021', '2022', '2023']

            for _ in range(5):
                product = Product.objects.create(
                    name=fake.random_element(elements=product_names),
                    model=fake.random_element(elements=product_modeles),
                    release_date=fake.date_between(start_date='-1y', end_date='+1y'),
                )
                product.nodes.add(node)

        Node.objects.rebuild()

        self.stdout.write(self.style.SUCCESS('Successfully filled the database with test data.'))

