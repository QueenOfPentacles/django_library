from django.shortcuts import render

# Create your views here.
from .models import Book, Author, BookInstance, Genre


def index(request):
    """
    View function for home page of site.
    """
    # Generate counts of some of the main objects
    num_books=Book.objects.all().count()
    num_genres=Genre.objects.all().count()
    num_instances=BookInstance.objects.all().count()
    num_intros=Book.objects.filter(title__icontains='intro').count()

    # Available books (status = 'a')
    num_instances_available=BookInstance.objects.filter(status__exact='a').count()
    num_authors=Author.objects.count()  # The 'all()' is implied by default.

    # Number of visits to this view, as counted in the session variable.
    num_visits=request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits+1

    # Render the HTML template index.html with the data in the context variable
    return render(
        request,
        'index.html',
        context={'num_books':num_books,'num_genres':num_genres,'num_instances':num_instances,'num_intros':num_intros,'num_instances_available':num_instances_available,'num_authors':num_authors,'num_visits':num_visits},
    )

from django.views import generic

class BookListView(generic.ListView):
    model = Book
    paginate_by = 5

class BookDetailView(generic.DetailView):
    model = Book
	
class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 5

class AuthorDetailView(generic.DetailView):
    model = Author

from django.contrib.auth.mixins import LoginRequiredMixin

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """
    Generic class-based view listing books on loan to current user. 
    """
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 5
    
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

from django.contrib.auth.mixins import PermissionRequiredMixin

class LoanedBooksAllListView(PermissionRequiredMixin,generic.ListView):
    """
    Generic class-based view listing all books on loan visible only to users with can_mark_returned permission.
    """
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name ='catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 5

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


from django.contrib.auth.decorators import permission_required

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime

from .forms import RenewBookForm

@permission_required('catalog.can_mark_returned')  
    #This decorator checks whether a user has a particular permission. Permission names take the form "<app label>.<permission codename>" (e.g. polls.can_vote is a permission on a model in the polls application). The decorator may also take an iterable of permissions, in which case the user must have all of the permissions in order to access the view.

def renew_book_librarian(request, pk):
   
    #View function for renewing a specific BookInstance by librarian
    
    book_inst=get_object_or_404(BookInstance, pk = pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})

from django.contrib.auth.decorators import permission_required	
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Book

class BookCreate(PermissionRequiredMixin,CreateView):
    model = Book
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'
    template_name ='catalog/book_form.html'


class BookAllListView(PermissionRequiredMixin,generic.ListView):
    model = Book
    permission_required = 'catalog.can_mark_returned'
    template_name ='catalog/book_list_all.html'
    paginate_by = 10


class BookUpdate(PermissionRequiredMixin,UpdateView):
    model = Book
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'


class BookDelete(PermissionRequiredMixin,DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalog.can_mark_returned'



	
from django.contrib.auth.decorators import permission_required	
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author

class AuthorCreate(PermissionRequiredMixin,CreateView):

    #the PermissionRequiredMixin checks whether the user accessing a view has all given permissions. You should specify the permission (or an iterable of permissions,in which case the user must have all of the permissions in order to access the view.) using the permission_required parameter: permission_required = 'polls.can_vote', or for multiple permissions:  permission_required = ('polls.can_open', 'polls.can_edit')

    model = Author
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'
    template_name ='catalog/author_form.html'


class AuthorAllListView(PermissionRequiredMixin,generic.ListView):
    model = Author
    permission_required = 'catalog.can_mark_returned'
    template_name ='catalog/author_list_all.html'
    paginate_by = 10


class AuthorUpdate(PermissionRequiredMixin,UpdateView):
    model = Author
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'


class AuthorDelete(PermissionRequiredMixin,DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.can_mark_returned'




