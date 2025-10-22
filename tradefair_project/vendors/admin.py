# """
# Admin configuration for the vendors app in the TradeFair project.

# Registers the Shed model for administration in the Django admin interface.
# """

# from django.contrib import admin
# from .models import Shed

# @admin.register(Shed)
# class ShedAdmin(admin.ModelAdmin):
#     """
#     Admin configuration for the Shed model.

#     Attributes:
#         list_display (tuple): Fields to display in the admin list view.
#         search_fields (tuple): Fields to search in the admin interface.
#         list_filter (tuple): Fields to filter in the admin interface.
#     """
#     list_display = ('shed_number', 'name', 'vendor', 'domain', 'secured')
#     search_fields = ('shed_number', 'name', 'vendor__user__username')
#     list_filter = ('domain', 'secured')

#     def get_queryset(self, request):
#         """
#         Optimize queryset by selecting related vendor and user.

#         Args:
#             request: HTTP request.

#         Returns:
#             QuerySet: Optimized Shed queryset.
#         """
#         return super().get_queryset(request).select_related('vendor__user')