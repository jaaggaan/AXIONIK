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
  useEffect(() => {
    let isMounted = true;
    const fetchLiveData = async () => {
      try {
        const res = await fetch("http://localhost:63265/api/customers");
        if (res.ok) {
          const data = await res.json();
          if (data && data.success && Array.isArray(data.customers) && isMounted) {
            const apiCusts: Customer[] = data.customers.map((c: any) => ({
              id: c.id || `FC-${Math.floor(Math.random() * 90000)}`,
              name: c.username || c.name || "First Citizen Member",
              email: c.email || "",
              phone: c.phone || c.phone_number || "",
              loyaltyTier: (c.loyaltyTier || c.vip_tier || "Black") as LoyaltyTier,
              loyaltyPoints: Number(c.loyaltyPoints || c.points || 1250),
              totalSpent: Number(c.totalSpent || c.total_spend || c.lifetimeSpend || 125000),
              totalOrders: Number(c.totalOrders || c.ordersCount || 10),
              lastPurchaseDate: "2026-08-02",
              preferredCategory: c.preferredCategory || "Luxury Watches & Accessories",
              joinedDate: "2026-01-15",
              avatar: c.avatar || "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=150",
              storeLocation: c.storeLocation || "Mumbai - Malad West Flagship"
            }));

            setCustomers(prev => {
              if (!Array.isArray(prev)) return prev;
              const merged = [...prev];
              apiCusts.forEach(ac => {
                if (ac && ac.email) {
                  const existingIdx = merged.findIndex(m => m && m.email && m.email.toLowerCase() === ac.email.toLowerCase());
                  if (existingIdx !== -1) {
                    merged[existingIdx] = { ...merged[existingIdx], ...ac };
                  } else {
                    merged.unshift(ac);
                  }
                }
              });
              return merged;
            });
          }
        }
      } catch (e) {}

      try {
        const resR = await fetch("http://localhost:63265/api/redemptions");
        if (resR.ok) {
          const dataR = await resR.json();
          if (dataR && dataR.success && Array.isArray(dataR.redemptions) && isMounted) {
            const redemptionsList: any[] = dataR.redemptions;
            setCoupons(prevCoupons => {
              if (!Array.isArray(prevCoupons)) return prevCoupons;
              return prevCoupons.map(cpn => {
                if (!cpn || !cpn.code) return cpn;
                const matched = redemptionsList.filter(r => r.couponCode && r.couponCode.toUpperCase() === cpn.code.toUpperCase());
                if (matched.length > 0) {
                  const formattedReds: CouponRedemption[] = matched.map(r => ({
                    id: r.id || `RED-${Math.floor(Math.random() * 90000)}`,
                    couponId: cpn.id,
                    couponCode: cpn.code,
                    customerName: r.customerName || "Wi-Fi Shopper",
                    customerEmail: r.customerEmail || "",
                    customerPhone: r.customerPhone || "",
                    loyaltyTier: "Black",
                    orderId: r.orderId || `SS-ORD-${Math.floor(90000 + Math.random() * 9999)}`,
                    orderTotal: Number(r.orderTotal || cpn.minOrderValue + 500),
                    discountSaved: Number(r.discountSaved || cpn.discountValue),
                    redeemedAt: r.redeemedAt || "Today",
                    storeLocation: r.storeLocation || "Mumbai - Malad West Flagship"
                  }));

                  const existingReds = cpn.redemptions || [];
                  const mergedReds = [
                    ...formattedReds.filter(fr => !existingReds.some(er => er.customerEmail && er.customerEmail.toLowerCase() === fr.customerEmail.toLowerCase())),
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
    };

    fetchLiveData();
    const interval = setInterval(fetchLiveData, 1000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);



  // Live API Sync Hook for Customers
  useEffect(() => {
    const fetchLiveCustomers = async () => {
      try {
        const res = await fetch("http://localhost:63265/api/customers");
        if (res.ok) {
          const data = await res.json();
          if (data.success && Array.isArray(data.customers)) {
            const apiCusts = data.customers.map((c: any) => ({
              id: c.id || `FC-${Math.floor(Math.random() * 90000)}`,
              name: c.username || c.name || "First Citizen Member",
              email: c.email || "",
              phone: c.phone || c.phone_number || "",
              loyaltyTier: c.loyaltyTier || c.vip_tier || "Black",
              lifetimeSpend: c.totalSpent || c.total_spend || 125000,
              points: c.loyaltyPoints || 1250,
              preferredCategory: c.preferredCategory || "Luxury Watches",
              joinedDate: "2026-01-15",
              storeLocation: c.storeLocation || "Mumbai - Malad West Flagship"
            }));

            setCustomers(prev => {
              const merged = [...prev];
              apiCusts.forEach(ac => {
                if (ac.email && !merged.some(m => m.email.toLowerCase() === ac.email.toLowerCase())) {
                  merged.unshift(ac);
                }
              });
              return merged;
            });
          }
        }
      } catch (e) {}
    };

    fetchLiveCustomers();
    const interval = setInterval(fetchLiveCustomers, 1000);
    return () => clearInterval(interval);
  }, []);

  const [inventory, setInventory] = useState<InventoryItem[]>(INITIAL_INVENTORY);
  const [coupons, setCoupons] = useState<Coupon[]>(INITIAL_COUPONS);
  const [returns, setReturns] = useState<ReturnRecord[]>(INITIAL_RETURNS);

  // Poll Telemetry Sync API on Port 5000 every 1 second
  useEffect(() => {
    const fetchSyncedData = async () => {
      try {
        // Fetch Orders from Port 5000 API
        const ordRes = await fetch('http://localhost:63265/api/orders');
        if (ordRes.ok) {
          const ordData = await ordRes.json();
          if (ordData.success && Array.isArray(ordData.orders)) {
            setOrders(ordData.orders);
          }
        }
      } catch (e) {}

      try {
        // Fetch Customers from Port 5000 API
        const custRes = await fetch('http://localhost:63265/api/customers');
        if (custRes.ok) {
          const data = await custRes.json();
          if (data.success && Array.isArray(data.customers)) {
            setCustomers(data.customers);
          }
        }
      } catch (e) {}

      try {
        // Fetch Coupons from Port 5000 API
        const cpnRes = await fetch('http://localhost:63265/api/coupons');
        if (cpnRes.ok) {
          const cpnData = await cpnRes.json();
          if (cpnData.success && Array.isArray(cpnData.coupons)) {
            const serverCoupons = cpnData.coupons;
            setCoupons(prevCoupons => {
              // Merge server coupons keeping existing redemptions intact
              return serverCoupons.map((sc: any) => {
                const existing = prevCoupons.find(pc => pc.code.toUpperCase() === sc.code.toUpperCase());
                return {
                  id: sc.id || `CPN-${Date.now()}`,
                  code: sc.code.toUpperCase(),
                  description: sc.description || 'Promotional Offer',
                  discountType: sc.discountType || 'Percentage',
                  discountValue: Number(sc.discountValue) || 10,
                  minOrderValue: Number(sc.minOrderValue) || 1999,
                  usageCount: sc.usageCount || (existing ? existing.usageCount : 0),
                  maxUsage: sc.maxUsage || 1000,
                  status: sc.status || 'Active',
                  startDate: sc.startDate || '2026-07-01',
                  endDate: sc.endDate || '2026-12-31',
                  applicableCategory: sc.applicableCategory || 'Site-wide',
                  redemptions: existing ? existing.redemptions : []
                };
              });
            });
          }
        }
      } catch (e) {}

      try {
        // Fetch Coupon Redemptions from Port 5000 API
        const redRes = await fetch('http://localhost:63265/api/redemptions');
        if (redRes.ok) {
          const data = await redRes.json();
          if (data.success && Array.isArray(data.redemptions)) {
            const apiRedemptions = data.redemptions;
            setCoupons(prevCoupons => {
              let updated = prevCoupons.map(cpn => {
                const matchingReds = apiRedemptions.filter((r: any) => r.couponCode.toUpperCase() === cpn.code.toUpperCase());
                if (matchingReds.length > 0) {
                  const formattedReds: CouponRedemption[] = matchingReds.map((r: any) => ({
                    id: r.id || `RED-${Date.now()}`,
                    couponId: cpn.id,
                    couponCode: cpn.code,
                    customerName: r.customerName,
                    customerEmail: r.customerEmail,
                    customerPhone: r.customerPhone,
                    loyaltyTier: 'Black',
                    orderId: r.orderId || `SS-ORD-${Math.floor(98000 + Math.random() * 999)}`,
                    orderTotal: r.orderTotal || (cpn.minOrderValue + 500),
                    discountSaved: r.discountSaved || (cpn.discountType === 'Percentage' ? Math.round((cpn.minOrderValue * cpn.discountValue) / 100) : cpn.discountValue),
                    redeemedAt: `${r.redeemedAt} (In-Store Kiosk)`,
                    storeLocation: 'Mumbai - Malad West Flagship'
                  }));

                  const existingReds = cpn.redemptions || [];
                  const unmerged = formattedReds.filter(fr => !existingReds.some(er => er.customerName.toLowerCase() === fr.customerName.toLowerCase() && er.couponCode === fr.couponCode));
                  const merged = [...unmerged, ...existingReds];

                  return {
                    ...cpn,
                    usageCount: Math.max(cpn.usageCount, merged.length),
                    redemptions: merged
                  };
                }
                return cpn;
              });

              // Also auto-add any unseen coupon codes from API redemptions
              apiRedemptions.forEach((r: any) => {
                const codeUpper = r.couponCode.toUpperCase();
                if (!updated.some(c => c.code.toUpperCase() === codeUpper)) {
                  updated.push({
                    id: `CPN-${Math.floor(200 + Math.random() * 800)}`,
                    code: codeUpper,
                    description: `Special Promotional Voucher - Code ${codeUpper}`,
                    discountType: 'Flat Amount',
                    discountValue: r.discountSaved || 500,
                    minOrderValue: r.orderTotal || 1999,
                    usageCount: 1,
                    maxUsage: 5000,
                    status: 'Active',
                    startDate: '2026-07-01',
                    endDate: '2026-12-31',
                    applicableCategory: 'Site-wide Kiosk',
                    redemptions: [
                      {
                        id: r.id || `RED-${Date.now()}`,
                        couponId: `CPN-DYNAMIC`,
                        couponCode: codeUpper,
                        customerName: r.customerName,
                        customerEmail: r.customerEmail,
                        customerPhone: r.customerPhone,
                        loyaltyTier: 'Black',
                        orderId: r.orderId || `SS-ORD-${Math.floor(98000 + Math.random() * 999)}`,
                        orderTotal: r.orderTotal || 4999,
                        discountSaved: r.discountSaved || 500,
                        redeemedAt: `${r.redeemedAt} (In-Store Kiosk)`,
                        storeLocation: 'Mumbai - Malad West Flagship'
                      }
                    ]
                  });
                }
              });

              return updated;
            });
          }
        }
      } catch (e) {}
    };

    fetchSyncedData();
    const interval = setInterval(fetchSyncedData, 1000);
    return () => clearInterval(interval);
  }, []);

  // Modals state
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [selectedInventoryItem, setSelectedInventoryItem] = useState<InventoryItem | null>(null);
  const [isOrderModalOpen, setIsOrderModalOpen] = useState(false);
  const [isOpenMobile, setIsOpenMobile] = useState(false);
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);
  const [isDownloadModalOpen, setIsDownloadModalOpen] = useState(false);

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
        return { sales: 892100, orders: 2420, returns: 145, custCount: 9 };
      default:
        // 'All Stores (Nationwide)'
        return { sales: 4892450, orders: 13100, returns: 866, custCount: customers.length };
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
              : orders.filter((o) => o.storeLocation === selectedStore || (selectedStore.includes('Mumbai') && (o.customerName === 'Ananya Deshmukh' || o.customerName === 'ricky' || o.customerName === 'JAGAN' || o.customerName === 'Mahima')));

            const filteredCustomers = selectedStore === 'All Stores (Nationwide)'
              ? customers
              : customers.filter((c) => (c as any).storeLocation === selectedStore || (! (c as any).storeLocation && selectedStore.includes('Mumbai')));

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
