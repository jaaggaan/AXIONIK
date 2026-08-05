/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { TabType, Order, OrderStatus, Customer, InventoryItem, Coupon, ReturnRecord, CouponRedemption } from './types';
import {
  INITIAL_ORDERS,
  INITIAL_CUSTOMERS,
  INITIAL_INVENTORY,
  INITIAL_COUPONS,
  INITIAL_RETURNS,
  STORE_LOCATIONS,
} from './data/mockData';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { OverviewTab } from './components/dashboard/OverviewTab';
import { OrdersTab } from './components/orders/OrdersTab';
import { CustomersTab } from './components/customers/CustomersTab';
import { InventoryTab } from './components/inventory/InventoryTab';
import { ReturnProductTab } from './components/returns/ReturnProductTab';
import { CouponsTab } from './components/coupons/CouponsTab';
import { CustomerFeedbackTab } from './components/feedback/CustomerFeedbackTab';
import { AnalyticsTab } from './components/analytics/AnalyticsTab';
import { ReportsTab } from './components/reports/ReportsTab';
import { HelpTab } from './components/help/HelpTab';
import { SettingsTab } from './components/settings/SettingsTab';
import { CommandPalette } from './components/modals/CommandPalette';
import { DownloadReportModal } from './components/modals/DownloadReportModal';

export default function App() {
  const [activeTab, setActiveTab] = useState<TabType>('dashboard');
  const [selectedStore, setSelectedStore] = useState<string>(STORE_LOCATIONS[1]);
  const [dateRange, setDateRange] = useState<string>('Today (Jul 27, 2026)');

  const [orders, setOrders] = useState<Order[]>(INITIAL_ORDERS);
  const [customers, setCustomers] = useState<Customer[]>(INITIAL_CUSTOMERS);

  
  // Safe Live API Sync Hook
  // Safe Live API Sync Hook
  // Safe Live API Sync Hook
  useEffect(() => {
    let isMounted = true;
    const fetchLiveData = async () => {
      // Fetch Live Customers
      try {
        const res63k = (await fetch("http://localhost:63265/api/customers").catch(() => null)) || (await fetch("/api/customers").catch(() => null));
        const res5k = res63k && res63k.ok ? null : await fetch("http://localhost:5000/api/customers").catch(() => null);
        const res = res63k && res63k.ok ? res63k : res5k;
        if (res && res.ok) {
          const data = await res.json();
          if (data && data.success && Array.isArray(data.customers) && isMounted) {
            const apiCusts: Customer[] = data.customers.map((c: any) => {
              const rawSpend = c.totalSpent ?? c.total_spend ?? c.lifetimeSpend;
              const rawPoints = c.loyaltyPoints ?? c.points;
              return {
                id: c.id || c.user_id || c.customer_id || `FC-${Math.floor(Math.random() * 90000)}`,
                name: c.name || c.username || "First Citizen Member",
                email: c.email || "",
                phone: c.phone || c.phone_number || "",
                loyaltyTier: (c.loyaltyTier || c.vip_tier || "Black First Citizen") as LoyaltyTier,
                loyaltyPoints: typeof rawPoints === 'number' ? rawPoints : Number(rawPoints || 1250),
                totalSpent: typeof rawSpend === 'number' ? rawSpend : Number(rawSpend || 125000),
                totalOrders: Number(c.totalOrders || c.ordersCount || 1),
                lastPurchaseDate: c.lastPurchaseDate || c.last_visit || "Today",
                preferredCategory: c.preferredCategory || "Online E-Commerce",
                joinedDate: c.joinedDate || "2026-01-15",
                avatar: c.avatar || "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=150",
                storeLocation: c.storeLocation || "Online Store (eCom Direct)"
              };
            });

            setCustomers(prev => {
              if (!Array.isArray(prev)) return prev;
              const merged = [...prev];
              apiCusts.forEach(ac => {
                if (!ac) return;
                const existingIdx = merged.findIndex(m => 
                  (m.email && ac.email && m.email.trim() !== "" && m.email.toLowerCase() === ac.email.toLowerCase()) ||
                  (m.phone && ac.phone && m.phone.trim() !== "" && m.phone === ac.phone) ||
                  (m.name && ac.name && m.name.trim().toLowerCase() === ac.name.trim().toLowerCase())
                );
                if (existingIdx !== -1) {
                  merged[existingIdx] = { ...merged[existingIdx], ...ac };
                } else {
                  merged.unshift(ac);
                }
              });
              return merged;
            });
          }
        }
      } catch (e) {}

      // Fetch Live Orders
      try {
        const resO63k = (await fetch("http://localhost:63265/api/orders").catch(() => null)) || (await fetch("/api/orders").catch(() => null));
        const resO5k = resO63k && resO63k.ok ? null : await fetch("http://localhost:5000/api/orders").catch(() => null);
        const resO = resO63k && resO63k.ok ? resO63k : resO5k;
        if (resO && resO.ok) {
          const dataO = await resO.json();
          if (dataO && dataO.success && Array.isArray(dataO.orders) && isMounted) {
            const apiOrders: Order[] = dataO.orders.map((o: any) => ({
              id: o.id || o.orderId || `ORD-${Math.floor(Math.random()*90000)}`,
              orderId: o.orderId || o.id || `SS-ORD-${Math.floor(Math.random()*90000)}`,
              customerName: o.customerName || "Shoppers Stop Guest",
              customerPhone: o.customerPhone || "",
              customerEmail: o.customerEmail || "",
              items: Array.isArray(o.items) ? o.items : [{ title: "Online Purchase", qty: 1, price: Number(o.totalAmount || 0) }],
              totalAmount: Number(o.totalAmount || o.orderTotal || 0),
              couponCode: o.couponCode || "",
              discountSaved: Number(o.discountSaved || 0),
              paymentMethod: o.paymentMethod || "Razorpay Verified",
              status: (o.status || "CONFIRMED") as OrderStatus,
              storeLocation: o.storeLocation || "Online Store (eCom Direct)",
              date: o.date || o.order_date || "Today"
            }));

            setOrders(prev => {
              const merged = [...prev];
              apiOrders.forEach(ao => {
                const idx = merged.findIndex(m => m.orderId === ao.orderId || m.id === ao.id);
                if (idx !== -1) {
                  merged[idx] = { ...merged[idx], ...ao };
                } else {
                  merged.unshift(ao);
                }
              });
              return merged;
            });
          }
        }
      } catch (e) {}

      // Fetch Live Coupons
      try {
        const resR = await fetch("http://localhost:63265/api/redemptions").catch(() => null);
        if (resR && resR.ok) {
          const dataR = await resR.json();
          if (dataR && dataR.success && Array.isArray(dataR.redemptions) && isMounted) {
            const redemptionsList: any[] = dataR.redemptions;
            setCoupons(prevCoupons => {
              if (!Array.isArray(prevCoupons)) return prevCoupons;
              return prevCoupons.map(cpn => {
                if (!cpn || !cpn.code) return cpn;
                const cleanCpnCode = cpn.code.replace(/\s+/g, '').toUpperCase();
                const matched = redemptionsList.filter(r => {
                  if (!r || !r.couponCode) return false;
                  return r.couponCode.replace(/\s+/g, '').toUpperCase() === cleanCpnCode;
                });
                if (matched.length > 0) {
                  const formattedReds: CouponRedemption[] = matched.map(r => ({
                    id: r.id || `RED-${Math.floor(Math.random() * 90000)}`,
                    couponId: cpn.id,
                    couponCode: cpn.code,
                    customerName: r.customerName || r.name || "Wi-Fi Shopper",
                    customerEmail: r.customerEmail || r.email || "",
                    customerPhone: r.customerPhone || r.phone || "",
                    loyaltyTier: r.loyaltyTier || "Black First Citizen",
                    orderId: r.orderId || `SS-ORD-${Math.floor(90000 + Math.random() * 9999)}`,
                    orderTotal: Number(r.orderTotal || cpn.minOrderValue + 500),
                    discountSaved: Number(r.discountSaved || cpn.discountValue),
                    redeemedAt: r.redeemedAt || "Today",
                    storeLocation: r.storeLocation || "Online Store (eCom Direct)"
                  }));

                  const existingReds = cpn.redemptions || [];
                  const mergedReds = [
                    ...formattedReds.filter(fr => !existingReds.some(er => 
                      (er.id && fr.id && er.id === fr.id) ||
                      (er.orderId && fr.orderId && er.orderId === fr.orderId) ||
                      (er.customerName && fr.customerName && er.customerName.trim().toLowerCase() === fr.customerName.trim().toLowerCase())
                    )),
                    ...existingReds
                  ];
                  return {
                    ...cpn,
                    usageCount: Math.max(cpn.usageCount, mergedReds.length),
                    redemptions: mergedReds
                  };
                }
                return cpn;
              });
            });
          }
        }
      } catch (e) {}

      try {
        const resC = await fetch("http://localhost:63265/api/coupons");
        if (resC.ok) {
          const dataC = await resC.json();
          if (dataC && dataC.success && Array.isArray(dataC.coupons) && isMounted) {
            const serverCoupons = dataC.coupons;
            setCoupons(prevCoupons => {
              if (!Array.isArray(prevCoupons)) return prevCoupons;
              const merged = [...prevCoupons];
              serverCoupons.forEach((sc: any) => {
                if (!sc || !sc.code) return;
                const cleanCode = sc.code.toString().replace(/\s+/g, '').toUpperCase();
                const idx = merged.findIndex(pc => pc && pc.code && pc.code.toString().replace(/\s+/g, '').toUpperCase() === cleanCode);
                // Merge server redemptions with any already in local state (dedup by id / orderId / customerName)
                const serverReds: CouponRedemption[] = (sc.redemptions || []).map((r: any) => ({
                  id: r.id || `RED-${Math.floor(Math.random() * 90000)}`,
                  couponId: sc.id || '',
                  couponCode: sc.code.toUpperCase(),
                  customerName: r.customerName || 'Wi-Fi Shopper',
                  customerEmail: r.customerEmail || '',
                  customerPhone: r.customerPhone || '',
                  loyaltyTier: r.loyaltyTier || 'Gold',
                  orderId: r.orderId || `SS-ORD-${Math.floor(90000 + Math.random() * 9999)}`,
                  orderTotal: Number(r.orderTotal || 0),
                  discountSaved: Number(r.discountSaved || 0),
                  redeemedAt: r.redeemedAt || 'Today',
                  storeLocation: r.storeLocation || 'Mumbai - Malad West Flagship'
                }));
                const existingReds = idx !== -1 ? (merged[idx].redemptions || []) : [];
                const mergedReds = [
                  ...serverReds.filter(sr => !existingReds.some(er =>
                    (er.id && sr.id && er.id === sr.id) ||
                    (er.orderId && sr.orderId && er.orderId === sr.orderId) ||
                    (er.customerName && sr.customerName && er.customerName.trim().toLowerCase() === sr.customerName.trim().toLowerCase())
                  )),
                  ...existingReds
                ];
                const formatted = {
                  id: sc.id || `CPN-${Date.now()}`,
                  code: sc.code.toUpperCase(),
                  description: sc.description || 'Promotional Offer',
                  discountType: sc.discountType || 'Percentage',
                  discountValue: Number(sc.discountValue) || 10,
                  minOrderValue: Number(sc.minOrderValue) || 1999,
                  usageCount: Math.max(sc.usageCount || 0, idx !== -1 ? merged[idx].usageCount : 0, mergedReds.length),
                  maxUsage: sc.maxUsage || 1000,
                  status: sc.status || 'Active',
                  startDate: sc.startDate || '2026-07-01',
                  endDate: sc.endDate || '2026-12-31',
                  applicableCategory: sc.applicableCategory || 'Site-wide',
                  redemptions: mergedReds
                };
                if (idx !== -1) {
                  merged[idx] = { ...merged[idx], ...formatted, redemptions: mergedReds };
                } else {
                  merged.push(formatted);
                }
              });
              return merged;
            });
          }
        }
      } catch (e) {}
    };

    fetchLiveData();
    const interval = setInterval(fetchLiveData, 10000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const [inventory, setInventory] = useState<InventoryItem[]>(INITIAL_INVENTORY);
  const [coupons, setCoupons] = useState<Coupon[]>(INITIAL_COUPONS);
  const [returns, setReturns] = useState<ReturnRecord[]>(INITIAL_RETURNS);

  

  // Modals state
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [selectedInventoryItem, setSelectedInventoryItem] = useState<InventoryItem | null>(null);
  const [isOrderModalOpen, setIsOrderModalOpen] = useState(false);
  const [isOpenMobile, setIsOpenMobile] = useState(false);
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);
  const [isDownloadModalOpen, setIsDownloadModalOpen] = useState(false);

  // Dynamically calculate online sales and order totals
  const onlineOrders = orders.filter(o => 
    o.storeLocation === 'Online Store (eCom Direct)' || 
    (o as any).channel === 'Online E-Commerce' || 
    (o as any).channel === 'Online Storefront' ||
    !o.storeLocation ||
    o.storeLocation === 'Online Storefront'
  );

  const onlineSalesSum = onlineOrders.reduce((sum, o) => sum + Number(o.totalAmount || 0), 0);
  const allOrdersSalesSum = orders.reduce((sum, o) => sum + Number(o.totalAmount || 0), 0);

  const getStoreMetrics = (store: string) => {
    switch (store) {
      case 'Mumbai - Malad West Flagship':
        return { sales: 1428900, orders: 3840, returns: 240, custCount: 14 };
      case 'Bengaluru - MG Road Metro':
        return { sales: 1145600, orders: 3120, returns: 195, custCount: 11 };
      case 'Delhi - Select CITYWALK Saket':
        return { sales: 1289200, orders: 3450, returns: 210, custCount: 12 };
      case 'Kolkata - South City Mall':
        return { sales: 568400, orders: 1480, returns: 110, custCount: 8 };
      case 'Hyderabad - Inorbit Mall Hitec City':
        return { sales: 460350, orders: 1210, returns: 111, custCount: 6 };
      case 'Online Store (eCom Direct)':
        return { 
          sales: 871110 + onlineSalesSum, 
          orders: 2420 + onlineOrders.length, 
          returns: 145, 
          custCount: customers.length 
        };
      default:
        // 'All Stores (Nationwide)'
        return { 
          sales: 4892450 + allOrdersSalesSum, 
          orders: 13100 + orders.length, 
          returns: 866, 
          custCount: customers.length 
        };
    }
  };

  const storeBase = getStoreMetrics(selectedStore);
  const approvedReturnsRefunds = returns
    .filter((r) => r.status === 'Approved')
    .reduce((sum, r) => sum + r.refundAmount, 0);

  const totalSales = Math.max(0, storeBase.sales - approvedReturnsRefunds);
  const totalOrders = storeBase.orders;
  const totalProducts = inventory.reduce((sum, item) => sum + item.stock, 0);
  const totalCustomers = storeBase.custCount;
  const approvedReturnsCount = returns.filter((r) => r.status === 'Approved').length;
  const totalReturns = storeBase.returns + approvedReturnsCount;

  const dashboardMetrics = {
    totalSales,
    totalOrders,
    totalProducts,
    totalCustomers,
    totalReturns,
  };

  const handleViewOrderDetails = (order: Order) => {
    setActiveTab('orders');
    setSelectedOrder(order);
    setIsOrderModalOpen(true);
  };

  const handleSelectCustomerFromSearch = (customer: Customer) => {
    setActiveTab('customers');
    setSelectedCustomer(customer);
  };

  const handleSelectInventoryFromSearch = (item: InventoryItem) => {
    setActiveTab('inventory');
    setSelectedInventoryItem(item);
  };

  const handleUpdateOrderStatus = (orderId: string, newStatus: OrderStatus) => {
    setOrders((prev) =>
      prev.map((o) => (o.id === orderId ? { ...o, status: newStatus } : o))
    );
    if (selectedOrder && selectedOrder.id === orderId) {
      setSelectedOrder((prev) => (prev ? { ...prev, status: newStatus } : null));
    }
  };

  const handleUpdateStock = (itemId: string, newStock: number) => {
    setInventory((prev) =>
      prev.map((item) => {
        if (item.id === itemId) {
          let status: 'In Stock' | 'Low Stock' | 'Out of Stock' = 'In Stock';
          if (newStock === 0) status = 'Out of Stock';
          else if (newStock <= item.minThreshold) status = 'Low Stock';
          return { ...item, stock: newStock, status };
        }
        return item;
      })
    );
  };

  const handleCreateCoupon = (newCoupon: Coupon) => {
    setCoupons((prev) => [newCoupon, ...prev]);
  };

  const handleEnrollCustomer = (newCustomer: Customer) => {
    setCustomers((prev) => [newCustomer, ...prev]);
  };

  const handleProcessReturn = (newReturnData: Omit<ReturnRecord, 'id'>) => {
    const newRecord: ReturnRecord = {
      ...newReturnData,
      id: `RET-2026-${String(returns.length + 1).padStart(3, '0')}`,
      createdAt: new Date().toISOString(),
    };

    setReturns((prev) => [newRecord, ...prev]);

    if (newReturnData.status === 'Approved' && newReturnData.restockInventory) {
      setInventory((prev) =>
        prev.map((item) => {
          const nameMatch = item.name.toLowerCase() === newReturnData.productName.toLowerCase();
          const skuMatch = newReturnData.sku && item.sku.toLowerCase() === newReturnData.sku.toLowerCase();

          if (nameMatch || skuMatch) {
            const updatedStock = item.stock + newReturnData.quantity;
            let status: 'In Stock' | 'Low Stock' | 'Out of Stock' = 'In Stock';
            if (updatedStock === 0) status = 'Out of Stock';
            else if (updatedStock <= item.minThreshold) status = 'Low Stock';
            return { ...item, stock: updatedStock, status };
          }
          return item;
        })
      );
    }
  };

  const getPageTitle = () => {
    switch (activeTab) {
      case 'dashboard':
        return 'Executive Retail Dashboard';
      case 'orders':
        return 'Omnichannel Orders';
      case 'customers':
        return 'First Citizen CRM';
      case 'inventory':
        return 'Inventory Telemetry';
      case 'return_product':
        return 'Return Product Module';
      case 'coupons':
        return 'Promotions & Coupons';
      case 'analytics':
        return 'Analytics & Intelligence';
      case 'reports':
        return 'Financial Reports';
      case 'help':
        return 'Store Ops Help Desk';
      case 'settings':
        return 'Store Settings';
      default:
        return 'Dashboard';
    }
  };

  return (
    <div className="min-h-screen bg-[#F9FAFB] text-gray-900 font-sans selection:bg-[#E11D48]/20 selection:text-[#E11D48]">
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        selectedStore={selectedStore}
        setSelectedStore={setSelectedStore}
        isOpenMobile={isOpenMobile}
        setIsOpenMobile={setIsOpenMobile}
      />

      <div className="lg:pl-64 flex flex-col min-h-screen transition-all duration-300">
        <Header
          title={getPageTitle()}
          onOpenMobileSidebar={() => setIsOpenMobile(true)}
          onOpenCommandPalette={() => setIsCommandPaletteOpen(true)}
          onOpenDownloadModal={() => setIsDownloadModalOpen(true)}
          dateRange={dateRange}
          setDateRange={setDateRange}
        />

        <main className="flex-1 p-4 sm:p-6 md:p-8 max-w-7xl w-full mx-auto">
          {(() => {
            const filteredOrders = selectedStore === 'All Stores (Nationwide)'
              ? orders
              : selectedStore === 'Online Store (eCom Direct)'
              ? orders.filter((o) => o.storeLocation === 'Online Store (eCom Direct)' || (o as any).channel === 'Online E-Commerce' || !o.storeLocation)
              : orders.filter((o) => o.storeLocation === selectedStore);

            const filteredCustomers = selectedStore === 'All Stores (Nationwide)'
              ? customers
              : selectedStore === 'Online Store (eCom Direct)'
              ? customers.filter((c) => (c as any).storeLocation === 'Online Store (eCom Direct)' || (c as any).preferredCategory === 'Online E-Commerce' || !(c as any).storeLocation)
              : customers.filter((c) => (c as any).storeLocation === selectedStore);

            return (
              <>
                {activeTab === 'dashboard' && (
                  <OverviewTab
                    orders={filteredOrders}
                    onNavigateTab={setActiveTab}
                    onViewOrderDetails={handleViewOrderDetails}
                    selectedStore={selectedStore}
                    metrics={dashboardMetrics}
                  />
                )}

                {activeTab === 'orders' && (
                  <OrdersTab
                    orders={filteredOrders}
                    onViewOrderDetails={handleViewOrderDetails}
                    onUpdateOrderStatus={handleUpdateOrderStatus}
                    selectedOrderFromSearch={selectedOrder}
                  />
                )}

                {activeTab === 'customers' && (
                  <CustomersTab
                    customers={filteredCustomers}
                    onEnrollCustomer={handleEnrollCustomer}
                    selectedCustomerFromSearch={selectedCustomer}
                  />
                )}

                {activeTab === 'inventory' && (
                  <InventoryTab
                    inventory={inventory}
                    onUpdateStock={handleUpdateStock}
                    selectedItemFromSearch={selectedInventoryItem}
                    selectedStore={selectedStore}
                  />
                )}
              </>
            );
          })()}

          {activeTab === 'return_product' && (
            <ReturnProductTab
              returns={returns}
              orders={orders}
              inventory={inventory}
              onProcessReturn={handleProcessReturn}
            />
          )}

          {activeTab === 'coupons' && (
            <CouponsTab coupons={coupons} onCreateCoupon={handleCreateCoupon} />
          )}

          {activeTab === 'feedback' && <CustomerFeedbackTab />}

          {activeTab === 'analytics' && <AnalyticsTab />}

          {activeTab === 'reports' && <ReportsTab />}

          {activeTab === 'help' && <HelpTab />}

          {activeTab === 'settings' && (
            <SettingsTab
              selectedStore={selectedStore}
              setSelectedStore={setSelectedStore}
            />
          )}
        </main>
      </div>

      <CommandPalette
        isOpen={isCommandPaletteOpen}
        onClose={() => setIsCommandPaletteOpen(false)}
        orders={orders}
        customers={customers}
        inventory={inventory}
        onSelectTab={setActiveTab}
        onSelectOrder={handleViewOrderDetails}
        onSelectCustomer={handleSelectCustomerFromSearch}
        onSelectInventory={handleSelectInventoryFromSearch}
      />

      <DownloadReportModal
        isOpen={isDownloadModalOpen}
        onClose={() => setIsDownloadModalOpen(false)}
      />
    </div>
  );
}
