"use client";

import { useState } from 'react';

interface PaymentModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: (amount: number) => void;
}

export default function PaymentModal({ isOpen, onClose, onSuccess }: PaymentModalProps) {
    const [amount, setAmount] = useState("50000");
    const [method, setMethod] = useState("upi");
    const [processing, setProcessing] = useState(false);

    if (!isOpen) return null;

    const handlePayment = async () => {
        setProcessing(true);
        // Simulate gateway delay
        await new Promise(resolve => setTimeout(resolve, 2000));
        setProcessing(false);
        onSuccess(parseFloat(amount));
        onClose();
    };

    return (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="bg-white text-gray-900 rounded-2xl w-[400px] overflow-hidden shadow-2xl">
                {/* Header */}
                <div className="bg-blue-600 p-6 text-white flex justify-between items-center">
                    <div>
                        <h3 className="text-xl font-bold">Add Funds</h3>
                        <p className="text-blue-100 text-xs">Secure Payment Gateway</p>
                    </div>
                    <div className="bg-white/20 p-2 rounded-lg">
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
                    </div>
                </div>

                {/* Body */}
                <div className="p-6">
                    <div className="mb-6">
                        <label className="block text-xs font-bold text-gray-500 uppercase mb-2">Amount (₹)</label>
                        <input
                            type="number"
                            value={amount}
                            onChange={(e) => setAmount(e.target.value)}
                            className="w-full text-3xl font-bold border-b-2 border-gray-200 focus:border-blue-600 outline-none py-2 text-gray-800"
                        />
                    </div>

                    <div className="mb-6">
                        <label className="block text-xs font-bold text-gray-500 uppercase mb-2">Payment Method</label>
                        <div className="grid grid-cols-2 gap-3">
                            <button
                                onClick={() => setMethod("upi")}
                                className={`p-3 rounded-lg border flex flex-col items-center gap-2 transition-all ${method === "upi" ? "border-blue-600 bg-blue-50 text-blue-700" : "border-gray-200 hover:border-gray-300"}`}
                            >
                                <span className="font-bold">UPI</span>
                                <span className="text-xs text-gray-500">GPay, PhonePe</span>
                            </button>
                            <button
                                onClick={() => setMethod("card")}
                                className={`p-3 rounded-lg border flex flex-col items-center gap-2 transition-all ${method === "card" ? "border-blue-600 bg-blue-50 text-blue-700" : "border-gray-200 hover:border-gray-300"}`}
                            >
                                <span className="font-bold">Card</span>
                                <span className="text-xs text-gray-500">Visa, MasterCard</span>
                            </button>
                        </div>
                    </div>

                    <button
                        onClick={handlePayment}
                        disabled={processing}
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 rounded-xl transition-all flex items-center justify-center gap-2"
                    >
                        {processing ? (
                            <>
                                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                Processing...
                            </>
                        ) : (
                            <>Pay ₹{parseFloat(amount).toLocaleString()}</>
                        )}
                    </button>

                    <button onClick={onClose} className="w-full mt-4 text-gray-400 text-sm hover:text-gray-600">Cancel Transaction</button>
                </div>

                <div className="bg-gray-50 p-3 text-center text-xs text-gray-400 border-t">
                    Powered by <span className="font-bold text-gray-500">SecurePay</span>
                </div>
            </div>
        </div>
    );
}
