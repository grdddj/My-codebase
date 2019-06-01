function R = ApllyOperator(Field,Operator)
    R = zeros(size(Field));
    for i=2:size(Field,1)-1
        for j=2:size(Field,2)-1
            R(i,j)=sum(sum(Field(i-1:i+1,j-1:j+1).*Operator));
        end
    end

endfunction
