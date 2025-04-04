from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from xhtml2pdf import pisa
import io

# Pricing Plans Data
PRICING_PLANS = [
    {"name": "100% Interested Leads - 3,999-/", "ad_budget": 3000, "plan_price": 3999, "min_order": 10000, "mer": 10},
    {"name": "100% Interested Leads - 7,999-/", "ad_budget": 4000, "plan_price": 7999, "min_order": 999, "mer": 10},
    {"name": "100% Interested Leads - 14,999-/", "ad_budget": 6000, "plan_price": 14999, "min_order": 10000, "mer": 10},
    {"name": "100% Interested Leads - 27,999-/", "ad_budget": 8000, "plan_price": 27999, "min_order": 10000, "mer": 10},
    {"name": "100% Closed Leads - 30,000-/", "ad_budget": 6000, "plan_price": 30000, "min_order": 20000, "mer": 10},
    {"name": "100% Closed Leads - 60,000-/", "ad_budget": 8000, "plan_price": 60000, "min_order": 20000, "mer": 10},
]

# Home Page
def index(request):
    return render(request, "index.html")

# Fetch Best Pricing Plan
def pricing_details(request):
    min_order_value = float(request.GET.get("min_order_value", 0))

    pricing_plans_copy = [plan.copy() for plan in PRICING_PLANS]

    for plan in pricing_plans_copy:
        if min_order_value < 3000:
            plan["num_leads"] = max(round(plan["plan_price"] / (min_order_value * plan["mer"] / 100), 0) + 5, 10)
        else:
            plan["num_leads"] = round(plan["plan_price"] / (min_order_value * plan["mer"] / 100), 0)

        plan["ad_budget"] = int(plan["ad_budget"])
    
    sorted_plans = sorted(pricing_plans_copy, key=lambda x: abs(x["num_leads"] - 15))
    best_plan = sorted_plans[0]

    all_plans_data = [
        {
            "name": plan["name"],
            "numLeads": plan["num_leads"],
            "costPerLead": round(plan["plan_price"] / plan["num_leads"], 2) if plan["num_leads"] > 0 else 0,
            "adBudget": plan["ad_budget"]
        }
        for plan in pricing_plans_copy
    ]

    return JsonResponse({
        "bestPlan": best_plan["name"],
        "costPerLead": round(best_plan["plan_price"] / best_plan["num_leads"], 2) if best_plan["num_leads"] > 0 else 0,
        "allocationPercent": best_plan["mer"],
        "numLeads": best_plan["num_leads"],
        "allPlans": all_plans_data
    })

# Generate PDF Proposal
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from xhtml2pdf import pisa
import io

def generate_marketing_pdf(request):
    context = {
        "avg_order_value": request.GET.get("avgOrderValue", "N/A"),
        "package": request.GET.get("package", "N/A"),
        "ad_budget": request.GET.get("adBudget", "N/A"),
        "revenue": request.GET.get("revenue", "N/A"),
        "num_leads": request.GET.get("numLeads", "N/A"),
        "duration": request.GET.get("duration", "N/A"),
        "savings": request.GET.get("savings", "N/A"),
    }

    template = get_template("pdf_template.html")
    html = template.render(context)

    pdf_buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(html.encode("utf-8"), dest=pdf_buffer)  # Encode as UTF-8

    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)

    pdf_buffer.seek(0)
    response = HttpResponse(pdf_buffer, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="Marketing_Proposal.pdf"'
    return response
