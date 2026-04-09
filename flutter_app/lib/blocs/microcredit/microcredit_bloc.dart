import 'package:flutter_bloc/flutter_bloc.dart';

import '../../repositories/microcredit_repository.dart';
import 'microcredit_event.dart';
import 'microcredit_state.dart';

class MicrocreditBloc extends Bloc<MicrocreditEvent, MicrocreditState> {
  final MicrocreditRepository microcreditRepository;

  MicrocreditBloc({required this.microcreditRepository})
      : super(const MicrocreditInitial()) {
    on<CreditProfileLoadRequested>(_onCreditProfileLoadRequested);
    on<ProductsLoadRequested>(_onProductsLoadRequested);
    on<MicrocreditRequested>(_onMicrocreditRequested);
    on<MicrocreditsLoadRequested>(_onMicrocreditsLoadRequested);
    on<PaymentSubmitted>(_onPaymentSubmitted);
    on<ScoreRecalculateRequested>(_onScoreRecalculateRequested);
  }

  Future<void> _onCreditProfileLoadRequested(
    CreditProfileLoadRequested event,
    Emitter<MicrocreditState> emit,
  ) async {
    emit(const MicrocreditLoading());
    try {
      final profile = await microcreditRepository.getCreditProfile();
      emit(CreditProfileLoaded(profile: profile));
    } catch (e) {
      emit(MicrocreditError(message: e.toString()));
    }
  }

  Future<void> _onProductsLoadRequested(
    ProductsLoadRequested event,
    Emitter<MicrocreditState> emit,
  ) async {
    emit(const MicrocreditLoading());
    try {
      final products = await microcreditRepository.getProducts();
      emit(ProductsLoaded(products: products));
    } catch (e) {
      emit(MicrocreditError(message: e.toString()));
    }
  }

  Future<void> _onMicrocreditRequested(
    MicrocreditRequested event,
    Emitter<MicrocreditState> emit,
  ) async {
    emit(const MicrocreditLoading());
    try {
      final microcredit = await microcreditRepository.requestMicrocredit(
        productId: event.productId,
        amount: event.amount,
      );
      emit(MicrocreditCreated(microcredit: microcredit));
    } catch (e) {
      emit(MicrocreditError(message: e.toString()));
    }
  }

  Future<void> _onMicrocreditsLoadRequested(
    MicrocreditsLoadRequested event,
    Emitter<MicrocreditState> emit,
  ) async {
    emit(const MicrocreditLoading());
    try {
      final microcredits = await microcreditRepository.getMicrocredits();
      emit(MicrocreditsLoaded(microcredits: microcredits));
    } catch (e) {
      emit(MicrocreditError(message: e.toString()));
    }
  }

  Future<void> _onPaymentSubmitted(
    PaymentSubmitted event,
    Emitter<MicrocreditState> emit,
  ) async {
    emit(const MicrocreditLoading());
    try {
      await microcreditRepository.makePayment(
        microcreditId: event.microcreditId,
        amount: event.amount,
      );
      emit(const PaymentCompletedState());
    } catch (e) {
      emit(MicrocreditError(message: e.toString()));
    }
  }

  Future<void> _onScoreRecalculateRequested(
    ScoreRecalculateRequested event,
    Emitter<MicrocreditState> emit,
  ) async {
    emit(const MicrocreditLoading());
    try {
      final profile = await microcreditRepository.recalculateScore();
      emit(ScoreRecalculated(profile: profile));
    } catch (e) {
      emit(MicrocreditError(message: e.toString()));
    }
  }
}
