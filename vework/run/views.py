from django.http import JsonResponse
from django.shortcuts import render
import math
    
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from django.http import HttpResponse


PRICING_PLANS = [
    {"name": "100% Interested Leads - 3,999-/", "ad_budget":3000, "plan_price": 3999, "min_order": 10000, "mer": 10},
    {"name": "100% Interested Leads - 7,999-/", "ad_budget":4000, "plan_price": 7999, "min_order": 999, "mer": 10},
    {"name": "100% Interested Leads - 14,999-/", "ad_budget":6000, "plan_price": 14999, "min_order": 10000, "mer": 10},
    {"name": "100% Interested Leads - 27,999-/", "ad_budget":8000, "plan_price": 27999, "min_order": 10000, "mer": 10},
    {"name": "100% Closed Leads - 30,000-/", "ad_budget":6000, "plan_price": 30000, "min_order": 20000, "mer": 10},
    {"name": "100% Closed Leads - 60,000-/", "ad_budget":8000, "plan_price": 60000, "min_order": 20000, "mer": 10},
]



def index(request):
    return render(request, "index.html")


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


def generate_marketing_pdf(request):
    # Get data from GET parameters
    dm_proposal_plan = request.GET.get("dmProposalPlan", "N/A")
    ad_budget = request.GET.get("adBudget", "N/A")
    leads_provided = request.GET.get("leadsProvided", "N/A")
    duration = request.GET.get("duration", "N/A")
    profit_per_lead = request.GET.get("profitPerLead", "N/A")
    expected_profit = request.GET.get("expectedProfit", "N/A")
    cost_per_lead = request.GET.get("costPerLead", "N/A")

    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Digital_Marketing_Proposal.pdf"'

    # Create PDF
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, height - 50, "Digital Marketing Proposal")

    p.setFont("Helvetica", 12)
    p.drawString(100, height - 100, f"DM Proposal Plan: {dm_proposal_plan}")
    p.drawString(100, height - 120, f"Ad Budget: ₹{ad_budget}")
    p.drawString(100, height - 140, f"Leads Provided: {leads_provided}")
    p.drawString(100, height - 160, f"Duration of Leads: {duration} Days")
    p.drawString(100, height - 180, f"Profit Per Lead: ₹{profit_per_lead}")
    p.drawString(100, height - 200, f"Expected Profit: ₹{expected_profit}")
    p.drawString(100, height - 220, f"Cost Per Lead: ₹{cost_per_lead}")

    p.showPage()
    p.save()
    
    return response