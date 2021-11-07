from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login,logout
from .forms import CustomerSignUpForm,VendorSignUpForm,CustomerForm,VendorForm
from django.contrib.auth.decorators import login_required
from collections import Counter
from django.urls import reverse
from django.db.models import Q
from .models import Customer,Vendor,Item,Menu,Order,orderItem,User
from django.http import HttpResponse
import geocoder
from math import sin, cos, sqrt, atan2, radians

def index(request):
	return render(request,'webapp/index.html',{})

def orderplaced(request):
	return render(request,'webapp/orderplaced.html',{})

def loc(a,b,lat,lag):
	R = 6373.0
	lat1 = radians(a)
	lon1 = radians(b)
	lat2 = radians(lat)
	lon2 = radians(lag)

	dlon = lon2 - lon1
	dlat = lat2 - lat1

	a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
	c = 2 * atan2(sqrt(a), sqrt(1 - a))

	distance = R * c
	print(distance)
	return distance

def vendor(request):
	v_object = Vendor.objects.all()
	g = geocoder.ip('me')
	lat = g.latlng[0]
	lag = g.latlng[1]
	r = []
	for i in v_object:
		a = i.lat
		b = i.lng
		if loc(a,b,lat,lag)<1.5:
			r.append(i)
	query 	= request.GET.get('q')
	if query:
		v_object=Vendor.objects.filter(Q(rname__icontains=query)).distinct()
		return render(request,'webapp/vendor.html',{'r_object':v_object})
	return render(request,'webapp/vendor.html',{'r_object':r})


def Logout(request):
	if request.user.is_vendor:
		logout(request)
		return redirect("rlogin")
	else:
		logout(request)
		return redirect("login")


def customerRegister(request):
	form =CustomerSignUpForm(request.POST or None)
	if form.is_valid():
		user      = form.save(commit=False)
		username  =	form.cleaned_data['username']
		password  = form.cleaned_data['password']
		user.is_customer=True
		user.set_password(password)
		user.save()
		user = authenticate(username=username,password=password)
		if user is not None:
			if user.is_active:
				login(request,user)
				return redirect("ccreate")
	context ={
		'form':form
	}			
	return render(request,'webapp/signup.html',context)


def customerLogin(request):
	if request.method=="POST":
		username = request.POST['username']
		password = request.POST['password']
		user     = authenticate(username=username,password=password)
		if user is not None:
			if user.is_active:
				login(request,user)
				return redirect("profile")
			else:
				return render(request,'webapp/login.html',{'error_message':'Your account disable'})
		else:
			return render(request,'webapp/login.html',{'error_message': 'Invalid Login'})
	return render(request,'webapp/login.html')


def customerProfile(request,pk=None):
	if pk:
		user = User.objects.get(pk=pk)
	else:
		user=request.user
	
	return render(request,'webapp/profile.html',{'user':user})


def createCustomer(request):
	form = CustomerForm(request.POST or None)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.user = request.user
		instance.save()
		return redirect("profile")
	context={
	'form':form,
	'title':"Complete Your profile"
	}
	return render(request,'webapp/profile_form.html',context)


def updateCustomer(request,id):
	form  	 = CustomerForm(request.POST or None,instance=request.user.customer)
	if form.is_valid():
		form.save()
		return redirect('profile')
	context={
	'form':form,
	'title':"Update Your profile"
	}
	return render(request,'webapp/profile_form.html',context)

def vendorMenu(request,pk=None):

	menu = Menu.objects.filter(v_id=pk)
	vend = Vendor.objects.filter(id=pk)

	items =[]
	for i in menu:
		item = Item.objects.filter(fname=i.item_id)
		for content in item:
			temp=[]
			temp.append(content.fname)
			temp.append(content.category)
			temp.append(i.price)
			temp.append(i.id)
			temp.append(vend[0].status)
			temp.append(i.quantity)
			temp.append(i.description)
			temp.append(i.item_img.url)
			items.append(temp)
	context = {
		'items'	: items,
		'rid' 	: pk,
		'vname'	: vend[0].vname,
		'vmin'	: vend[0].min_ord,
		'vinfo' : vend[0].info,
		'vlocation':vend[0].location,
	}
	return render(request,'webapp/menu.html',context)


@login_required(login_url='/login/user/')
def checkout(request):
	if request.POST:
		addr  = request.POST['address']
		ordid = request.POST['oid']
		Order.objects.filter(id=int(ordid)).update(delivery_addr = addr,
                                                    status=Order.ORDER_STATE_PLACED)
		return redirect('/orderplaced/')
	else:	
		cart = request.COOKIES['cart'].split(",")
		cart = dict(Counter(cart))
		items = []
		totalprice = 0
		uid = User.objects.filter(username=request.user)
		oid = Order()
		oid.orderedBy = uid[0]
		for x,y in cart.items():
			item = []
			it = Menu.objects.filter(id=int(x))
			if len(it):
				oiid=orderItem()
				oiid.item_id=it[0]
				oiid.quantity=int(y)
				oid.v_id=it[0].v_id
				oid.save()
				oiid.ord_id =oid
				oiid.save()
				totalprice += int(y)*it[0].price
				item.append(it[0].item_id.fname)
				it[0].quantity = it[0].quantity - y
				it[0].save()
				item.append(y)
				item.append(it[0].price*int(y))
			
			items.append(item)
		oid.total_amount=totalprice
		oid.save()
		context={
			"items":items,
			"totalprice":totalprice,
			"oid":oid.id
		}	
		return render(request,'webapp/order.html',context)

@login_required(login_url='/login/user/')
def orders(request):
	orders = Order.objects.filter(orderedBy = request.user)
	#return HttpResponse(orders)
	l=[]
	for order in orders:
		a=[]
		a.append(order)
		#return HttpResponse(a)
		orderitem = orderItem.objects.filter(ord_id = order)
		c=[]
		for items in orderitem:
			b=[]
			menu = Menu.objects.filter(id=items.item_id.id)
			b.append(items)
			b.append(menu[0])
			c.append(b)
			#return HttpResponse(b)
		a.append(c)
		l.append(a)
	return render(request,"webapp/customerorder.html",{"l":l})
	return HttpResponse(l)


def vendorRegister(request):
	form =VendorSignUpForm(request.POST or None)
	if form.is_valid():
		user      = form.save(commit=False)
		username  =	form.cleaned_data['username']
		password  = form.cleaned_data['password']
		user.is_vendor=True
		user.set_password(password)
		user.save()
		user = authenticate(username=username,password=password)
		if user is not None:
			if user.is_active:
				login(request,user)
				return redirect("rcreate")
	context ={
		'form':form
	}			
	return render(request,'webapp/vendorsignup.html',context)	


def vendorLogin(request):
	if request.method=="POST":
		username = request.POST['username']
		password = request.POST['password']
		user     = authenticate(username=username,password=password)
		if user is not None:
			if user.is_active:
				login(request,user)
				return redirect("rprofile")
			else:
				return render(request,'webapp/vendorlogin.html',{'error_message':'Your account disable'})
		else:
			return render(request,'webapp/vendorlogin.html',{'error_message': 'Invalid Login'})
	return render(request,'webapp/vendorlogin.html')


def vendorProfile(request,pk=None):
	if pk:
		user = User.objects.get(pk=pk)
	else:
		user=request.user
	
	return render(request,'webapp/vendor_profile.html',{'user':user})

@login_required(login_url='/login/vendor/')
def createVendor(request):
	form=VendorForm(request.POST or None,request.FILES or None)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.user = request.user
		instance.save()
		return redirect("rprofile")
	context={
	'form':form,
	'title':"Complete Your Vendor profile"
	}
	return render(request,'webapp/vendor_profile_form.html',context)

@login_required(login_url='/login/vendor/')
def updateVendor(request,id):
	form  	 = VendorForm(request.POST or None,request.FILES or None,instance=request.user.vendor)
	if form.is_valid():
		form.save()
		return redirect('rprofile')
	context={
	'form':form,
	'title':"Update Your Vendor profile"
	}
	return render(request,'webapp/vendor_profile_form.html',context)


@login_required(login_url='/login/vendor/')		
def menuManipulation(request):
	if not request.user.is_authenticated:
		return redirect("rlogin") 
		
	rest=Vendor.objects.filter(id=request.user.vendor.id);
	rest=rest[0]
	if request.POST:
		type=request.POST['submit']
		if type =="Modify":
			menuid = int(request.POST['menuid'])
			if request.FILES:
				#print("dnvjkdbkj")
				menu= Menu.objects.get(id=menuid)
				menu.item_img = request.FILES.get('myfile')
				menu.price = int(request.POST['price'])
				menu.description = request.POST['description']
				menu.quantity = int(request.POST['quantity'])
				menu.save()
			else:
				menu= Menu.objects.get(id=menuid)
				menu.item_img = menu.item_img
				menu.price = int(request.POST['price'])
				menu.description = request.POST['description']
				menu.quantity = int(request.POST['quantity'])
				menu.save()
		elif type == "Add" :
			itemid=int(request.POST['item'])
			item=Item.objects.filter(id=itemid)
			item=item[0]
			menu=Menu()
			menu.item_id=item
			menu.v_id=rest
			menu.price=int(request.POST['price'])
			menu.quantity=int(request.POST['quantity'])
			menu.description=request.POST['description']
			menu.item_img = request.FILES.get('myfile')
			menu.save()
		else:
			menuid = int(request.POST['menuid'])
			menu = Menu.objects.filter(id=menuid)
			menu[0].delete()

	menuitems=Menu.objects.filter(v_id=rest)
	menu=[]
	for x in menuitems:
		cmenu=[]
		cmenu.append(x.item_id)
		cmenu.append(x.price)
		cmenu.append(x.quantity)
		cmenu.append(x.id)
		cmenu.append(x.description)
		cmenu.append(x.item_img.url)
		menu.append(cmenu)

	menuitems = Item.objects.all()
	items = []
	for y in menuitems:
		citem = []
		citem.append(y.id)
		citem.append(y.fname)
		items.append(citem)

	context={
		"menu":menu,
		"items":items,
		"username":request.user.username,
	}
	return render(request,'webapp/menu_modify.html',context)

def orderlist(request):
	if request.POST:
		oid = request.POST['orderid']
		select = request.POST['orderstatus']
		select = int(select)
		order = Order.objects.filter(id=oid)
		if len(order):
			x = Order.ORDER_STATE_WAITING
			if select == 1:
				x = Order.ORDER_STATE_PLACED
			elif select == 2:
				x = Order.ORDER_STATE_ACKNOWLEDGED
			elif select == 3:
				x = Order.ORDER_STATE_COMPLETED
			elif select == 4:
				x = Order.ORDER_STATE_DISPATCHED
			elif select == 5:
				x = Order.ORDER_STATE_CANCELLED
			else:
				x = Order.ORDER_STATE_WAITING
			order[0].status = x
			order[0].save()

	orders = Order.objects.filter(v_id=request.user.vendor.id).order_by('-timestamp')
	corders = []

	for order in orders:

		user = User.objects.filter(id=order.orderedBy.id)
		user = user[0]
		corder = []
		if user.is_vendor:
			corder.append(user.vendor.vname)
			corder.append(user.vendor.info)
		else:
			corder.append(user.customer.f_name)
			corder.append(user.customer.phone)
		items_list = orderItem.objects.filter(ord_id=order)

		items = []
		for item in items_list:
			citem = []
			citem.append(item.item_id)
			citem.append(item.quantity)
			menu = Menu.objects.filter(id=item.item_id.id)
			citem.append(menu[0].price*item.quantity)
			menu = 0
			items.append(citem)

		corder.append(items)
		corder.append(order.total_amount)
		corder.append(order.id)

		x = order.status
		if x == Order.ORDER_STATE_WAITING:
		    continue
		elif x == Order.ORDER_STATE_PLACED:
		    x = 1
		elif x == Order.ORDER_STATE_ACKNOWLEDGED:
			x = 2
		elif x == Order.ORDER_STATE_COMPLETED:
			x = 3
		elif x == Order.ORDER_STATE_DISPATCHED:
			x = 4
		elif x == Order.ORDER_STATE_CANCELLED:
			x = 5
		else:
			continue

		corder.append(x)
		corder.append(order.delivery_addr)
		corders.append(corder)

	context = {
		"orders" : corders,
	}

	return render(request,"webapp/order-list.html",context)